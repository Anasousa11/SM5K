from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MembershipPlan, Membership, Event, EventRegistration, ClientProfile, TrainerProfile

# Class-based views

class HomeView(TemplateView):
    template_name = 'home.html'

class MembershipPlansView(ListView):
    model = MembershipPlan
    template_name = 'membership_plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        if hasattr(self.request.user, 'client_profile'):
            trainer = self.request.user.client_profile.primary_trainer
            return MembershipPlan.objects.filter(trainer=trainer, is_active=True)
        return MembershipPlan.objects.filter(is_active=True)

class EventsView(ListView):
    model = Event
    template_name = 'events.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = Event.objects.filter(date__gte=timezone.now().date(), is_cancelled=False)
        if hasattr(self.request.user, 'client_profile'):
            trainer = self.request.user.client_profile.primary_trainer
            queryset = queryset.filter(trainer=trainer)
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(event_type=type_filter)
        min_distance = self.request.GET.get('min_distance')
        if min_distance:
            try:
                queryset = queryset.filter(distance_km__gte=float(min_distance))
            except ValueError:
                pass
        max_distance = self.request.GET.get('max_distance')
        if max_distance:
            try:
                queryset = queryset.filter(distance_km__lte=float(max_distance))
            except ValueError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_filter'] = self.request.GET.get('type')
        context['min_distance'] = self.request.GET.get('min_distance')
        context['max_distance'] = self.request.GET.get('max_distance')
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        if hasattr(self.request.user, 'client_profile') and event.trainer != self.request.user.client_profile.primary_trainer:
            messages.error(self.request, "You can only view events from your trainer.")
            return redirect('events')
        registration = EventRegistration.objects.filter(user=self.request.user, event=event).first()
        context['registration'] = registration
        return context

    def post(self, request, *args, **kwargs):
        event = self.get_object()
        if 'join' in request.POST:
            if not request.user.client_profile.has_active_membership:
                messages.error(request, "You need an active membership to join events.")
                return redirect('event_detail', event_id=event.id)
            if event.is_full or event.is_past:
                messages.error(request, "Cannot join this event.")
                return redirect('event_detail', event_id=event.id)
            if EventRegistration.objects.filter(user=request.user, event=event).exists():
                messages.error(request, "Already registered.")
                return redirect('event_detail', event_id=event.id)
            EventRegistration.objects.create(user=request.user, event=event)
            messages.success(request, "Joined the event!")
            return redirect('event_detail', event_id=event.id)
        elif 'cancel' in request.POST:
            registration = EventRegistration.objects.filter(user=request.user, event=event).first()
            if registration:
                registration.status = 'cancelled'
                registration.save()
                messages.success(request, "Cancelled registration.")
            return redirect('event_detail', event_id=event.id)
        return self.get(request, *args, **kwargs)

# Function-based views for auth and specific logic

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def activate_membership(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    profile = request.user.client_profile
    if plan.trainer != profile.primary_trainer:
        messages.error(request, "You can only join plans from your trainer.")
        return redirect('membership_plans')
    if profile.has_active_membership:
        messages.error(request, "You already have an active membership.")
        return redirect('membership_plans')
    membership = Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=timezone.now().date()
    )
    messages.success(request, f"Membership {plan.name} activated!")
    return redirect('dashboard')

@login_required
def dashboard(request):
    profile = request.user.client_profile
    active_membership = profile.active_membership
    upcoming_registrations = EventRegistration.objects.filter(
        user=request.user,
        event__date__gte=timezone.now().date(),
        status='booked'
    ).select_related('event')[:3]
    return render(request, 'dashboard.html', {
        'active_membership': active_membership,
        'upcoming_registrations': upcoming_registrations
    })

@login_required
def my_events(request):
    registrations = EventRegistration.objects.filter(user=request.user).select_related('event')
    return render(request, 'my_events.html', {'registrations': registrations})

# Trainer and Client Dashboards

def is_trainer(user):
    return user.is_staff

@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    trainer = request.user.trainer_profile
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

@login_required
def client_dashboard(request):
    user = request.user
    client_profile = user.client_profile

    membership = client_profile.active_membership
    events = Event.objects.filter(trainer=client_profile.primary_trainer, date__gte=timezone.now().date())
    my_registrations = EventRegistration.objects.filter(user=user)

    context = {
        "membership": membership,
        "upcoming_events": events[:5],
        "my_registrations": my_registrations,
    }
    return render(request, "client/dashboard.html", context)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_memberships = Membership.objects.filter(status='active', end_date__gte=timezone.now().date()).count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date(), is_cancelled=False).count()
    registrations_next_week = EventRegistration.objects.filter(
        event__date__gte=timezone.now().date(),
        event__date__lte=timezone.now().date() + timedelta(days=7),
        status='booked'
    ).count()
    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'active_memberships': active_memberships,
        'upcoming_events': upcoming_events,
        'registrations_next_week': registrations_next_week
    })
