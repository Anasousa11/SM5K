# club/views.py

import json
import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .exercise_recommendations import generate_exercise_plan
from .forms import EventForm
from .models import (
    ClientProfile,
    Event,
    EventRegistration,
    Membership,
    MembershipPlan,
)

logger = logging.getLogger(__name__)


def is_trainer(user):
    return user.is_staff or getattr(user, "trainer_profile", None) is not None


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

        profile = None
        active_membership = None

        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, "client_profile", None)

        if profile:
            active_membership = getattr(profile, "active_membership", None)

        context["profile"] = profile
        context["active_membership"] = active_membership
        return context


@login_required
def activate_membership(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    profile = getattr(request.user, "client_profile", None)
    if not profile:
        messages.error(request, "You need a client profile to activate a membership.")
        return redirect("membership_plans")

    if getattr(profile, "has_active_membership", False):
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

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            logger.exception("Unhandled exception in EventsView.dispatch")
            messages.error(request, "Sorry, something went wrong loading events.")
            return redirect("home")

    def get_queryset(self):
        try:
            queryset = Event.objects.filter(
                date__gte=timezone.now().date(),
                is_cancelled=False,
            ).select_related("trainer", "trainer__user")

            if self.request.user.is_authenticated:
                profile = getattr(self.request.user, "client_profile", None)
                if profile:
                    trainer = getattr(profile, "primary_trainer", None)
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
        except Exception:
            logger.exception("EventsView.get_queryset failed")
            return Event.objects.none()

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["type_filter"] = self.request.GET.get("type")
            context["min_distance"] = self.request.GET.get("min_distance")
            context["max_distance"] = self.request.GET.get("max_distance")

            joined_ids = set()
            trainer_profile = None

            if self.request.user.is_authenticated:
                joined_ids = set(
                    EventRegistration.objects.filter(
                        user=self.request.user,
                        status="booked",
                    ).values_list("event_id", flat=True)
                )
                trainer_profile = getattr(self.request.user, "trainer_profile", None)

            context["joined_ids"] = joined_ids
            context["can_manage_events"] = is_trainer(self.request.user)
            context["trainer_profile"] = trainer_profile
            return context
        except Exception:
            logger.exception("EventsView.get_context_data failed")
            return super().get_context_data(**kwargs)


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = EventRegistration.objects.filter(
            user=self.request.user,
            event=self.object,
        ).first()
        context["registration"] = registration
        return context


@login_required
def create_event(request):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can create events.")
        return redirect("events")

    trainer_profile = getattr(request.user, "trainer_profile", None)

    if not request.user.is_staff and not trainer_profile:
        messages.error(request, "Trainer profile not found.")
        return redirect("trainer_dashboard")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if trainer_profile:
                event.trainer = trainer_profile
            event.save()
            messages.success(request, "Event created successfully.")
            return redirect("trainer_dashboard")
    else:
        form = EventForm()

    return render(
        request,
        "event_form.html",
        {
            "form": form,
            "page_title": "Create Event",
            "submit_text": "Create Event",
        },
    )


@login_required
def edit_event(request, event_id):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can edit events.")
        return redirect("events")

    trainer_profile = getattr(request.user, "trainer_profile", None)

    if request.user.is_staff:
        event = get_object_or_404(Event, id=event_id)
    else:
        event = get_object_or_404(Event, id=event_id, trainer=trainer_profile)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)
            if trainer_profile:
                updated_event.trainer = trainer_profile
            updated_event.save()
            messages.success(request, "Event updated successfully.")
            return redirect("trainer_dashboard")
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "event_form.html",
        {
            "form": form,
            "event": event,
            "page_title": "Edit Event",
            "submit_text": "Save Changes",
        },
    )


@login_required
def delete_event(request, event_id):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can delete events.")
        return redirect("events")

    trainer_profile = getattr(request.user, "trainer_profile", None)

    if request.user.is_staff:
        event = get_object_or_404(Event, id=event_id)
    else:
        event = get_object_or_404(Event, id=event_id, trainer=trainer_profile)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect("trainer_dashboard")

    return render(request, "event_confirm_delete.html", {"event": event})


@login_required
def join_event(request, event_id):
    if request.method != "POST":
        return redirect("events")

    profile = getattr(request.user, "client_profile", None)
    if not profile:
        messages.error(request, "Only clients can join events.")
        return redirect("events")

    if not getattr(profile, "has_active_membership", False):
        messages.error(request, "You need an active membership to join events.")
        return redirect("events")

    event = get_object_or_404(Event, id=event_id)

    if getattr(event, "is_full", False) or getattr(event, "is_past", False):
        messages.error(request, "You cannot join this event.")
        return redirect("events")

    registration, created = EventRegistration.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={"status": "booked"},
    )

    if not created and registration.status == "cancelled":
        registration.status = "booked"
        registration.save()

    messages.success(request, "You’ve joined this event.")
    return redirect("events")


@login_required
def leave_event(request, event_id):
    if request.method != "POST":
        return redirect("events")

    EventRegistration.objects.filter(user=request.user, event_id=event_id).delete()
    messages.success(request, "You’ve left this event.")
    return redirect("events")


# -------------------------
# AUTH & DASHBOARDS
# -------------------------

def register(request):
    return redirect("account_signup")


@login_required
def dashboard(request):
    if request.user.is_staff or getattr(request.user, "trainer_profile", None):
        return redirect("trainer_dashboard")
    if getattr(request.user, "client_profile", None):
        return redirect("client_dashboard")
    return redirect("home")


@login_required
def client_dashboard(request):
    profile = getattr(request.user, "client_profile", None)
    if not profile:
        messages.error(request, "You need a client profile.")
        return redirect("home")

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
            "membership": getattr(profile, "active_membership", None),
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

@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    trainer = getattr(request.user, "trainer_profile", None)

    clients = ClientProfile.objects.filter(primary_trainer=trainer)
    events = Event.objects.filter(trainer=trainer).order_by("date", "start_time")
    memberships = Membership.objects.filter(plan__trainer=trainer)

    return render(
        request,
        "trainer/dashboard.html",
        {
            "client_count": clients.count(),
            "event_count": events.count(),
            "active_memberships": memberships.filter(status="active").count(),
            "clients": clients[:10],
            "events": events,
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
                is_cancelled=False,
            ).count(),
        },
    )


# -------------------------
# EXERCISE RECOMMENDATIONS API
# -------------------------

@require_http_methods(["POST"])
@login_required
def get_exercise_recommendations(request):
    try:
        data = json.loads(request.body)
        weight_kg = float(data.get("weight_kg"))
        height_cm = float(data.get("height_cm"))
        goal = data.get("goal", "general_fitness")

        if weight_kg <= 0 or height_cm <= 0:
            return JsonResponse(
                {"success": False, "error": "Weight and height must be positive numbers"},
                status=400,
            )

        plan = generate_exercise_plan(weight_kg, height_cm, goal)

        return JsonResponse({"success": True, "data": plan})

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse(
            {"success": False, "error": f"Invalid request data: {str(e)}"},
            status=400,
        )
    except Exception as e:
        logger.exception("Exercise recommendations failed")
        return JsonResponse(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=500,
        )


@login_required
def exercise_plan_page(request):
    user_has_profile = getattr(request.user, "client_profile", None) is not None
    return render(request, "exercise_plan.html", {"user_has_profile": user_has_profile})
