from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.HomeView.as_view(), name="home"),

    # Auth / registration
    path("register/", views.register, name="register"),

    # Memberships
    path("membership-plans/", views.MembershipPlansView.as_view(), name="membership_plans"),
    path("activate-membership/<int:plan_id>/", views.activate_membership, name="activate_membership"),

    # Events
    path("events/", views.EventsView.as_view(), name="events"),
    path("events/<int:event_id>/", views.EventDetailView.as_view(), name="event_detail"),

    # Dashboards
    path("dashboard/", views.dashboard, name="dashboard"),
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("trainer/dashboard/", views.trainer_dashboard, name="trainer_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Client events
    path("my-events/", views.my_events, name="my_events"),
]
