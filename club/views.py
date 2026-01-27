from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from .models import (
    ClientProfile,
    Event,
    EventRegistration,
    Membership,
    MembershipPlan,
    TrainerProfile,
)


# ---------- Class-based views ----------

class HomeView(TemplateView):
    template_name = "home.html"


class MembershipPlansView(ListView):
    model = MembershipPlan
    template_name = "membership_plans.html"
    context_object_name = "plans"

    def get_queryset(self):
        return MembershipPlan.objects.filter(is_active=True).select_related("trainer")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_membership = None
        if self.request.user.is_authenticated and hasattr(self.request.user, "client_profile"):
            active_membership = self.request.user.client_profile.active_membership
        context["active_membership"] = active_membership
        return context


class EventsView(ListView):
    model = Event
    template_name = "events.html"
    context_object_name = "events"

    def get_queryset(self):
        queryset = Event.objects.filter(
            date__gte=timezone.now().date(), is_cancelled=False
        )

        # If the user is a client, only show events for their trainer (if set)
        if self.request.user.is_authenticated and hasattr(
            self.request.user, "client_profile"
        ):
            trainer = self.request.user.client_profile.primary_trainer
            if trainer:
                queryset = queryset.filter(trainer=trainer)

        # Filters
        type_filter = self.request.GET.get("type")
        if type_filter:
            queryset = queryset.filter(event_type=type_filter)

        min_distance = self.request.GET.get("min_distance")
        if min_distance:
            try:
                queryset = queryset.filter(distance_km__gte=float(min_distance))
            except ValueError:
                pass

        max_distance = self.request.GET.get("max_distance")
        if max_distance:
            try:
                queryset = queryset.filter(distance_km__lte=float(max_distance))
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_filter"] = self.request.GET.get("type")
        context["min_distance"] = self.request.GET.get("min_distance")
        context["max_distance"] = self.request.GET.get("max_distance")
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"

    def dispatch(self, request, *args, **kwargs):
        """
        Extra access control: if the user is a client and has a primary_trainer,
        only allow viewing events from that trainer.
        """
        self.object = self.get_object()
        event = self.object

        if request.user.is_authenticated and hasattr(request.user, "client_profile"):
            cp = request.user.client_profile
            if event.trainer and cp.primary_trainer and event.trainer != cp.primary_trainer:
                messages.error(request, "You can only view events from your trainer.")
                return redirect("events")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        registration = EventRegistration.objects.filter(
            user=self.request.user, event=event
        ).first()
        context["registration"] = registration
        return context

    def post(self, request, *args, **kwargs):
        event = self.get_object()

        # Join event
        if "join" in request.POST:
            if not hasattr(request.user, "client_profile"):
                messages.error(request, "You need a client profile to join events.")
                return redirect("event_detail", event_id=event.id)

            if not request.user.client_profile.has_active_membership:
                messages.error(request, "You need an active membership to join events.")
                return redirect("event_detail", event_id=event.id)

            if event.is_full or event.is_past:
                messages.error(request, "You cannot join this event.")
                return redirect("event_detail", event_id=event.id)

            if EventRegistration.objects.filter(
                user=request.user, event=event
            ).exists():
                messages.error(request, "You are already registered for this event.")
                return redirect("event_detail", event_id=event.id)

            EventRegistration.objects.create(user=request.user, event=event)
            messages.success(request, "You have joined this event.")
            return redirect("event_detail", event_id=event.id)

        # Cancel event
        if "cancel" in request.POST:
            registration = EventRegistration.objects.filter(
                user=request.user, event=event
            ).first()
            if registration:
                registration.status = "cancelled"
                registration.save()
                messages.success(request, "Your registration has been cancelled.")
            return redirect("event_detail", event_id=event.id)

        return self.get(request, *args, **kwargs)


# ---------- Auth & client views ----------

def register(request):
    """
    Simple registration:
    - creates a User
    - ensures a ClientProfile exists
    - logs the user in
    - sends them to the client dashboard
    """
    # if already logged in, don't allow registering a second account in same session
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Safe: if something else already created a ClientProfile, don't crash
            ClientProfile.objects.get_or_create(user=user)

            login(request, user)
            return redirect("client_dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    """
    Generic /dashboard/ route:
    - trainers → trainer_dashboard
    - clients → client_dashboard
    - others → home
    """
    if request.user.is_staff or hasattr(request.user, "trainer_profile"):
        return redirect("trainer_dashboard")
    elif hasattr(request.user, "client_profile"):
        return redirect("client_dashboard")
    return redirect("home")


@login_required
def activate_membership(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client profile to activate a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile

    # Optional: ensure the plan belongs to the client's trainer
    if plan.trainer and profile.primary_trainer and plan.trainer != profile.primary_trainer:
        messages.error(request, "You can only join plans from your trainer.")
        return redirect("membership_plans")

    if profile.has_active_membership:
        messages.error(request, "You already have an active membership.")
        return redirect("membership_plans")

    Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=timezone.now().date(),
    )
    messages.success(request, f"Membership '{plan.name}' activated!")
    return redirect("client_dashboard")


@login_required
def client_dashboard(request):
    user = request.user
    if not hasattr(user, "client_profile"):
        messages.error(request, "You need a client profile to view this page.")
        return redirect("home")

    client_profile = user.client_profile
    membership = client_profile.active_membership

    events = Event.objects.filter(
        trainer=client_profile.primary_trainer,
        date__gte=timezone.now().date(),
        is_cancelled=False,
    ).order_by("date")

    my_registrations = EventRegistration.objects.filter(user=user).select_related("event")

    context = {
        "membership": membership,
        "upcoming_events": events[:5],
        "my_registrations": my_registrations,
    }
    return render(request, "client/dashboard.html", context)


@login_required
def my_events(request):
    registrations = (
        EventRegistration.objects.filter(user=request.user)
        .select_related("event")
        .order_by("-booked_at")
    )
    return render(request, "my_events.html", {"registrations": registrations})


# ---------- Trainer & admin dashboards ----------

def is_trainer(user):
    return user.is_staff or hasattr(user, "trainer_profile")


@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    trainer = getattr(request.user, "trainer_profile", None)

    clients = ClientProfile.objects.none()
    events = Event.objects.none()
    memberships = Membership.objects.none()

    if trainer:
        clients = ClientProfile.objects.filter(primary_trainer=trainer)
        events = Event.objects.filter(trainer=trainer).order_by("date")
        memberships = Membership.objects.filter(plan__trainer=trainer)

    context = {
        "client_count": clients.count(),
        "event_count": events.count(),
        "active_memberships": memberships.filter(status="active").count(),
        "clients": clients[:10],
        "events": events[:5],
    }
    return render(request, "trainer/dashboard.html", context)


@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_memberships = Membership.objects.filter(
        status="active", end_date__gte=timezone.now().date()
    ).count()
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now().date(), is_cancelled=False
    ).count()
    registrations_next_week = EventRegistration.objects.filter(
        event__date__gte=timezone.now().date(),
        event__date__lte=timezone.now().date() + timedelta(days=7),
        status="booked",
    ).count()

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": total_users,
            "active_memberships": active_memberships,
            "upcoming_events": upcoming_events,
            "registrations_next_week": registrations_next_week,
        },
    )
