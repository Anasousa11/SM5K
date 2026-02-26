import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from club.models import MembershipPlan, Membership
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, plan_id):
    """
    Create a Stripe Checkout Session for purchasing a membership plan.
    """
    if request.method != "POST":
        return redirect("membership_plans")

    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client account to buy a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    if plan.trainer and profile.primary_trainer and plan.trainer != profile.primary_trainer:
        messages.error(request, "You can only buy plans from your trainer.")
        return redirect("membership_plans")

    if profile.has_active_membership:
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Stripe is not configured (missing STRIPE_SECRET_KEY).")
        return redirect("membership_plans")

    # Convert price to cents (USD)
    amount_cents = int(plan.price * 100)

    # Build success/cancel URLs for Stripe Checkout (append session id on success)
    success_url = request.build_absolute_uri(reverse("payments:payment_success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payments:payment_cancel"))

    # Build product_data safely
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

    # Avoid duplicates: check if membership already exists
    if hasattr(request.user, "client_profile") and request.user.client_profile.has_active_membership:
        messages.success(request, "Payment received. Your membership is already active.")
        return render(request, "payments/success.html", {"plan": plan})

    # Create membership
    Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=timezone.now().date(),
    )

    # Record payment
    Payment.objects.get_or_create(
        stripe_payment_intent_id=session.payment_intent,
        defaults={
            'user': request.user,
            'membership_plan': plan,
            'amount_cents': int(plan.price * 100),
            'status': 'succeeded',
            'paid_at': timezone.now(),
        }
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


@require_POST
def webhook(request):
    """
    Stripe webhook endpoint to handle asynchronous payment events.
    
    Verify webhook signature and process:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - charge.refunded
    
    Set STRIPE_WEBHOOK_SECRET in environment variables.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.__dict__.get('STRIPE_WEBHOOK_SECRET', '')
    
    if not webhook_secret:
        # Webhook secret not configured; log and accept to avoid breaking Stripe retries
        return JsonResponse({'warning': 'Webhook secret not configured'}, status=200)
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )
    except ValueError:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        _handle_payment_succeeded(intent)
    
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        _handle_payment_failed(intent)
    
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        _handle_charge_refunded(charge)
    
    return JsonResponse({'success': True})


def _handle_payment_succeeded(intent):
    """
    Process successful PaymentIntent:
    - Mark Payment record as succeeded
    - Activate Membership if not already done
    """
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent['id'])
        payment.mark_succeeded(charge_id=intent.get('latest_charge'))
        
        # Activate membership if not already done
        if payment.membership_plan:
            Membership.objects.get_or_create(
                user=payment.user,
                plan=payment.membership_plan,
                defaults={
                    'start_date': timezone.now().date(),
                    'status': 'active',
                }
            )
    except Payment.DoesNotExist:
        pass


def _handle_payment_failed(intent):
    """
    Process failed PaymentIntent: mark Payment record as failed.
    """
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=intent['id'])
        payment.mark_failed()
    except Payment.DoesNotExist:
        pass


def _handle_charge_refunded(charge):
    """
    Process refund: update Payment record status.
    """
    try:
        payment = Payment.objects.get(stripe_charge_id=charge['id'])
        payment.status = 'refunded'
        payment.save()
    except Payment.DoesNotExist:
        pass
