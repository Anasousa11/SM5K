# payments/views.py

from decimal import Decimal, ROUND_HALF_UP
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from club.models import MembershipPlan, Membership
from .models import Payment


def _to_cents(amount) -> int:
    """
    Convert Decimal/float/string pounds to integer pennies (or cents).
    """
    dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(dec * 100)


@login_required
@require_POST
def create_checkout_session(request, plan_id):
    """
    Create a Stripe Checkout Session for purchasing a membership plan.
    """
    if not getattr(settings, "STRIPE_SECRET_KEY", None):
        messages.error(request, "Stripe is not configured (missing STRIPE_SECRET_KEY).")
        return redirect("membership_plans")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    profile = getattr(request.user, "client_profile", None)
    if not profile:
        messages.error(request, "You need a client account to buy a membership.")
        return redirect("membership_plans")

    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    # If you restrict buying to a user's trainer, keep this
    if getattr(plan, "trainer", None) and getattr(profile, "primary_trainer", None):
        if plan.trainer != profile.primary_trainer:
            messages.error(request, "You can only buy plans from your trainer.")
            return redirect("membership_plans")

    if getattr(profile, "has_active_membership", False):
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    amount_cents = _to_cents(plan.price)

    success_url = request.build_absolute_uri(
        reverse("payments:payment_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payments:payment_cancel"))

    product_data = {"name": f"{plan.name} ({getattr(plan, 'billing_interval', 'monthly')})"}
    if getattr(plan, "description", "") and str(plan.description).strip():
        product_data["description"] = str(plan.description).strip()[:200]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": amount_cents,
                        "product_data": product_data,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "user_id": str(request.user.id),
                "plan_id": str(plan.id),
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(session.url, permanent=False)

    except Exception as e:
        messages.error(request, f"Stripe error: {e}")
        return redirect("membership_plans")


@login_required
def payment_success(request):
    """
    Handle successful Stripe Checkout payment.
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Missing payment session.")
        return redirect("membership_plans")

    if not getattr(settings, "STRIPE_SECRET_KEY", None):
        messages.error(request, "Stripe is not configured.")
        return redirect("membership_plans")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.error(request, "Could not verify payment. Please contact support.")
        return redirect("membership_plans")

    # Ensure this session belongs to the logged in user
    if str(session.metadata.get("user_id")) != str(request.user.id):
        messages.error(request, "This payment does not belong to your account.")
        return redirect("membership_plans")

    if session.payment_status != "paid":
        messages.error(request, "Payment not completed.")
        return redirect("membership_plans")

    plan_id = session.metadata.get("plan_id")
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    # Idempotent membership creation
    membership, _created = Membership.objects.get_or_create(
        user=request.user,
        plan=plan,
        defaults={
            "start_date": timezone.now().date(),
        },
    )

    # Record payment (idempotent)
    Payment.objects.get_or_create(
        stripe_payment_intent_id=session.payment_intent,
        defaults={
            "user": request.user,
            "membership_plan": plan,
            "amount_cents": _to_cents(plan.price),
            "status": "succeeded",
            "paid_at": timezone.now(),
        },
    )

    messages.success(request, "Payment successful. Membership activated!")
    return render(request, "payments/success.html", {"plan": plan})


@login_required
def payment_cancel(request):
    messages.error(request, "Payment cancelled or unsuccessful.")
    return render(request, "payments/cancel.html")


@csrf_exempt
@require_POST
def webhook(request):
    """
    Stripe webhook endpoint to handle asynchronous payment events.

    Set STRIPE_WEBHOOK_SECRET in Heroku config vars.
    """
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        # Accept so Stripe doesn't keep retrying forever
        return JsonResponse({"warning": "Webhook secret not configured"}, status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        _handle_payment_succeeded(data_object)

    elif event_type == "payment_intent.payment_failed":
        _handle_payment_failed(data_object)

    elif event_type == "charge.refunded":
        _handle_charge_refunded(data_object)

    return JsonResponse({"success": True})


def _handle_payment_succeeded(intent):
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent.get("id"))
    except Payment.DoesNotExist:
        return

    # If your model doesn't have mark_succeeded, just set fields directly:
    if hasattr(payment, "mark_succeeded"):
        payment.mark_succeeded(charge_id=intent.get("latest_charge"))
    else:
        payment.status = "succeeded"
        payment.stripe_charge_id = intent.get("latest_charge") or payment.stripe_charge_id
        payment.paid_at = payment.paid_at or timezone.now()
        payment.save()

    if payment.membership_plan:
        Membership.objects.get_or_create(
            user=payment.user,
            plan=payment.membership_plan,
            defaults={
                "start_date": timezone.now().date(),
            },
        )


def _handle_payment_failed(intent):
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent.get("id"))
    except Payment.DoesNotExist:
        return

    if hasattr(payment, "mark_failed"):
        payment.mark_failed()
    else:
        payment.status = "failed"
        payment.save()


def _handle_charge_refunded(charge):
    charge_id = charge.get("id")
    if not charge_id:
        return

    try:
        payment = Payment.objects.get(stripe_charge_id=charge_id)
    except Payment.DoesNotExist:
        return

    payment.status = "refunded"
    payment.save()