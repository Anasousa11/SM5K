import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from club.models import MembershipPlan, Membership
from .models import Payment


stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")


@login_required
@require_POST
def create_checkout_session(request, plan_id):
    """
    Create a Stripe Checkout Session for purchasing a membership plan.
    """
    if not stripe.api_key:
        messages.error(request, "Stripe is not configured (missing STRIPE_SECRET_KEY).")
        return redirect("membership_plans")

    # Must be a client
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client account to buy a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile

    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    # If plan is tied to a trainer, enforce it
    if plan.trainer and profile.primary_trainer and plan.trainer != profile.primary_trainer:
        messages.error(request, "You can only buy plans from your trainer.")
        return redirect("membership_plans")

    # Prevent buying if already active
    if getattr(profile, "has_active_membership", False):
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    # Stripe expects the smallest currency unit.
    # Your template shows £, but your Stripe code uses USD.
    # Pick ONE. For now we keep USD like your existing code.
    amount_cents = int(plan.price * 100)

    success_url = request.build_absolute_uri(
        reverse("payments:payment_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payments:payment_cancel"))

    product_data = {"name": f"{plan.name} ({plan.billing_interval})"}
    if plan.description and plan.description.strip():
        product_data["description"] = plan.description.strip()[:200]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
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

    # If membership already active, don't duplicate
    if hasattr(request.user, "client_profile") and getattr(request.user.client_profile, "has_active_membership", False):
        messages.success(request, "Payment received. Your membership is already active.")
        return render(request, "payments/success.html", {"plan": plan})

    # Create membership (adjust fields if your Membership model differs)
    Membership.objects.get_or_create(
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


@login_required
def payment_cancel(request):
    """
    Handle cancelled Stripe Checkout.
    """
    messages.error(request, "Payment cancelled or unsuccessful.")
    return render(request, "payments/cancel.html")


@csrf_exempt
@require_POST
def webhook(request):
    """
    Stripe webhook endpoint to handle async payment events.

    Requires STRIPE_WEBHOOK_SECRET in environment variables.
    """
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    # If you haven't configured the webhook secret yet, return 200
    # so Stripe doesn't retry forever while you're building.
    if not webhook_secret:
        return JsonResponse({"warning": "Webhook secret not configured"}, status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

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

    return JsonResponse({"success": True}, status=200)


def _handle_payment_succeeded(intent):
    """
    Process successful PaymentIntent:
    - Mark Payment record as succeeded
    - Activate Membership if not already active
    """
    intent_id = intent.get("id")
    if not intent_id:
        return

    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent_id)
    except Payment.DoesNotExist:
        return

    # If your Payment model has helper methods, use them; otherwise update directly
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
    """
    Process failed PaymentIntent: mark Payment record as failed.
    """
    intent_id = intent.get("id")
    if not intent_id:
        return

    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent_id)
    except Payment.DoesNotExist:
        return

    if hasattr(payment, "mark_failed"):
        payment.mark_failed()
    else:
        payment.status = "failed"
        payment.save()


def _handle_charge_refunded(charge):
    """
    Process refund: update Payment record status.
    """
    charge_id = charge.get("id")
    if not charge_id:
        return

    try:
        payment = Payment.objects.get(stripe_charge_id=charge_id)
    except Payment.DoesNotExist:
        return

    payment.status = "refunded"
    payment.save()