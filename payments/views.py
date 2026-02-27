import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from club.models import MembershipPlan, Membership
from .models import Payment


# Configure Stripe
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


# =========================
# CREATE CHECKOUT SESSION
# =========================
@login_required
def create_checkout_session(request, plan_id):
    if request.method != "POST":
        return redirect("membership_plans")

    if not stripe.api_key:
        messages.error(request, "Stripe is not configured.")
        return redirect("membership_plans")

    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client account to buy a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    # Prevent duplicate membership
    if getattr(profile, "has_active_membership", False):
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    amount_cents = int(plan.price * 100)

    success_url = request.build_absolute_uri(
        reverse("payments:payment_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("payments:payment_cancel")
    )

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": f"{plan.name} ({plan.billing_interval})",
                        },
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


# =========================
# PAYMENT SUCCESS
# =========================
@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, "Missing payment session.")
        return redirect("membership_plans")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.error(request, "Unable to verify payment.")
        return redirect("membership_plans")

    # Security check
    if str(session.metadata.get("user_id")) != str(request.user.id):
        messages.error(request, "Invalid payment session.")
        return redirect("membership_plans")

    if session.payment_status != "paid":
        messages.error(request, "Payment not completed.")
        return redirect("membership_plans")

    plan_id = session.metadata.get("plan_id")
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    # Prevent duplicate membership creation
    membership, created = Membership.objects.get_or_create(
        user=request.user,
        plan=plan,
        defaults={
            "start_date": timezone.now().date(),
        },
    )

    # Record payment
    Payment.objects.get_or_create(
        stripe_payment_intent_id=session.payment_intent,
        defaults={
            "user": request.user,
            "membership_plan": plan,
            "amount_cents": int(plan.price * 100),
            "status": "succeeded",
            "paid_at": timezone.now(),
        },
    )

    messages.success(request, "Payment successful. Membership activated!")
    return render(request, "payments/success.html", {"plan": plan})


# =========================
# PAYMENT CANCEL
# =========================
@login_required
def payment_cancel(request):
    messages.error(request, "Payment cancelled.")
    return render(request, "payments/cancel.html")


# =========================
# STRIPE WEBHOOK
# =========================
@require_POST
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    if not webhook_secret:
        return JsonResponse({"warning": "Webhook secret not configured"}, status=200)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret,
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        _handle_payment_succeeded(intent)

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        _handle_payment_failed(intent)

    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]
        _handle_charge_refunded(charge)

    return JsonResponse({"success": True})


# =========================
# WEBHOOK HELPERS
# =========================
def _handle_payment_succeeded(intent):
    try:
        payment = Payment.objects.get(
            stripe_payment_intent_id=intent["id"]
        )
        payment.status = "succeeded"
        payment.save()
    except Payment.DoesNotExist:
        pass


def _handle_payment_failed(intent):
    try:
        payment = Payment.objects.get(
            stripe_payment_intent_id=intent["id"]
        )
        payment.status = "failed"
        payment.save()
    except Payment.DoesNotExist:
        pass


def _handle_charge_refunded(charge):
    try:
        payment = Payment.objects.get(
            stripe_charge_id=charge["id"]
        )
        payment.status = "refunded"
        payment.save()
    except Payment.DoesNotExist:
        pass