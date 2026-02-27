# club/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.register, name="register"),

    path("membership-plans/", views.MembershipPlansView.as_view(), name="membership_plans"),
    path("activate-membership/<int:plan_id>/", views.activate_membership, name="activate_membership"),

    path("events/", views.EventsView.as_view(), name="events"),
    path("events/<int:event_id>/", views.EventDetailView.as_view(), name="event_detail"),
    path("events/<int:event_id>/join/", views.join_event, name="join_event"),
    path("events/<int:event_id>/leave/", views.leave_event, name="leave_event"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("trainer/dashboard/", views.trainer_dashboard, name="trainer_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("my-events/", views.my_events, name="my_events"),
    path("exercise-plan/", views.exercise_plan_page, name="exercise_plan"),
    path("api/exercise-recommendations/", views.get_exercise_recommendations, name="api_exercise_recommendations"),
]