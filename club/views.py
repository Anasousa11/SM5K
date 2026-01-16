from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import MembershipPlan, Membership, RunEvent, RunRegistration, MemberProfile

def home(request):
    return render(request, 'home.html')

def membership_plans(request):
    plans = MembershipPlan.objects.all()
    return render(request, 'membership_plans.html', {'plans': plans})

@login_required
def activate_membership(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)
    profile = request.user.member_profile
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

def run_events(request):
    events = RunEvent.objects.filter(date__gte=timezone.now().date(), is_cancelled=False)
    return render(request, 'run_events.html', {'events': events})

@login_required
def run_event_detail(request, event_id):
    event = get_object_or_404(RunEvent, id=event_id)
    registration = RunRegistration.objects.filter(user=request.user, event=event).first()
    if request.method == 'POST':
        if 'join' in request.POST:
            if not request.user.member_profile.has_active_membership:
                messages.error(request, "You need an active membership to join runs.")
                return redirect('run_event_detail', event_id=event.id)
            if event.is_full or event.is_past:
                messages.error(request, "Cannot join this run.")
                return redirect('run_event_detail', event_id=event.id)
            if registration:
                messages.error(request, "Already registered.")
                return redirect('run_event_detail', event_id=event.id)
            RunRegistration.objects.create(user=request.user, event=event)
            messages.success(request, "Joined the run!")
            return redirect('run_event_detail', event_id=event.id)
        elif 'cancel' in request.POST:
            if registration:
                registration.status = 'cancelled'
                registration.save()
                messages.success(request, "Cancelled registration.")
            return redirect('run_event_detail', event_id=event.id)
    return render(request, 'run_event_detail.html', {'event': event, 'registration': registration})

@login_required
def dashboard(request):
    profile = request.user.member_profile
    active_membership = profile.active_membership
    upcoming_registrations = RunRegistration.objects.filter(
        user=request.user,
        event__date__gte=timezone.now().date(),
        status='booked'
    ).select_related('event')[:3]
    return render(request, 'dashboard.html', {
        'active_membership': active_membership,
        'upcoming_registrations': upcoming_registrations
    })

@login_required
def my_runs(request):
    registrations = RunRegistration.objects.filter(user=request.user).select_related('event')
    return render(request, 'my_runs.html', {'registrations': registrations})

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_memberships = Membership.objects.filter(status='active', end_date__gte=timezone.now().date()).count()
    upcoming_events = RunEvent.objects.filter(date__gte=timezone.now().date(), is_cancelled=False).count()
    registrations_next_week = RunRegistration.objects.filter(
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
