import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from club.models import MembershipPlan, Membership


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, plan_id):
    if request.method != "POST":
        return redirect("membership_plans")

    # Must be a client to buy membership
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client account to buy a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    # Optional: only allow buying plans from your trainer (if both set)
    if plan.trainer and profile.primary_trainer and plan.trainer != profile.primary_trainer:
        messages.error(request, "You can only buy plans from your trainer.")
        return redirect("membership_plans")

    # Prevent buying if already active
    if profile.has_active_membership:
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Stripe is not configured (missing STRIPE_SECRET_KEY).")
        return redirect("membership_plans")

    # Decimal pounds -> integer pence
    amount_pence = int(plan.price * 100)

    success_url = request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payment_cancel"))

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": amount_pence,
                        "product_data": {
                            "name": f"{plan.name} ({plan.billing_interval})",
                            "description": (plan.description or "")[:200],
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
    except Exception:
        messages.error(request, "Could not start checkout. Please try again.")
        return redirect("membership_plans")

    return redirect(session.url, permanent=False)


@login_required
def payment_success(request):
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

    # Avoid duplicates
    if hasattr(request.user, "client_profile") and request.user.client_profile.has_active_membership:
        messages.success(request, "Payment received. Your membership is already active.")
        return render(request, "payments/success.html", {"plan": plan})

    Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=timezone.now().date(),
    )

    messages.success(request, "Payment successful. Membership activated!")
    return render(request, "payments/success.html", {"plan": plan})


@login_required
def payment_cancel(request):
    messages.error(request, "Payment cancelled or unsuccessful.")
    return render(request, "payments/cancel.html")
