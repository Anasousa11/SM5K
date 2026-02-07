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

# -------------------------
# BASIC PAGES
# -------------------------

class HomeView(TemplateView):
    template_name = "home.html"


# -------------------------
# MEMBERSHIPS
# -------------------------

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


@login_required
def activate_membership(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client profile to activate a membership.")
        return redirect("membership_plans")

    profile = request.user.client_profile

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


# -------------------------
# EVENTS
# -------------------------

class EventsView(ListView):
    model = Event
    template_name = "events.html"
    context_object_name = "events"

    def get_queryset(self):
        queryset = Event.objects.filter(
            date__gte=timezone.now().date(),
            is_cancelled=False
        )

        if self.request.user.is_authenticated and hasattr(self.request.user, "client_profile"):
            trainer = self.request.user.client_profile.primary_trainer
            if trainer:
                queryset = queryset.filter(trainer=trainer)

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
        joined_ids = set()
        if self.request.user.is_authenticated:
            joined_ids = set(
                EventRegistration.objects.filter(user=self.request.user)
                .values_list("event_id", flat=True)
            )
        context["joined_ids"] = joined_ids
        return context

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = EventRegistration.objects.filter(
            user=self.request.user,
            event=self.object
        ).first()
        context["registration"] = registration
        return context


@login_required
def join_event(request, event_id):
    if request.method != "POST":
        return redirect("events")

    if not hasattr(request.user, "client_profile"):
        messages.error(request, "Only clients can join events.")
        return redirect("events")

    if not request.user.client_profile.has_active_membership:
        messages.error(request, "You need an active membership to join events.")
        return redirect("events")

    event = get_object_or_404(Event, id=event_id)

    if event.is_full or event.is_past:
        messages.error(request, "You cannot join this event.")
        return redirect("events")

    EventRegistration.objects.get_or_create(user=request.user, event=event)
    messages.success(request, "You’ve joined this event.")
    return redirect("events")


@login_required
def leave_event(request, event_id):
    if request.method != "POST":
        return redirect("events")

    EventRegistration.objects.filter(
        user=request.user,
        event_id=event_id
    ).delete()

    messages.success(request, "You’ve left this event.")
    return redirect("events")


# -------------------------
# AUTH & DASHBOARDS
# -------------------------

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ClientProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect("client_dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.is_staff or hasattr(request.user, "trainer_profile"):
        return redirect("trainer_dashboard")
    elif hasattr(request.user, "client_profile"):
        return redirect("client_dashboard")
    return redirect("home")


@login_required
def client_dashboard(request):
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You need a client profile.")
        return redirect("home")

    profile = request.user.client_profile

    events = Event.objects.filter(
        trainer=profile.primary_trainer,
        date__gte=timezone.now().date(),
        is_cancelled=False,
    )

    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related("event")

    return render(
        request,
        "client/dashboard.html",
        {
            "membership": profile.active_membership,
            "upcoming_events": events[:5],
            "my_registrations": registrations,
        },
    )


@login_required
def my_events(request):
    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related("event")
    return render(request, "my_events.html", {"registrations": registrations})


# -------------------------
# TRAINER / ADMIN
# -------------------------

def is_trainer(user):
    return user.is_staff or hasattr(user, "trainer_profile")


@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    trainer = getattr(request.user, "trainer_profile", None)

    clients = ClientProfile.objects.filter(primary_trainer=trainer)
    events = Event.objects.filter(trainer=trainer)
    memberships = Membership.objects.filter(plan__trainer=trainer)

    return render(
        request,
        "trainer/dashboard.html",
        {
            "client_count": clients.count(),
            "event_count": events.count(),
            "active_memberships": memberships.filter(status="active").count(),
            "clients": clients[:10],
            "events": events[:5],
        },
    )


@staff_member_required
def admin_dashboard(request):
    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": User.objects.count(),
            "active_memberships": Membership.objects.filter(
                end_date__gte=timezone.now().date()
            ).count(),
            "upcoming_events": Event.objects.filter(
                date__gte=timezone.now().date(),
                is_cancelled=False
            ).count(),
        },
    )
