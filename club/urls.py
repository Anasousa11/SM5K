from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('membership-plans/', views.membership_plans, name='membership_plans'),
    path('activate-membership/<int:plan_id>/', views.activate_membership, name='activate_membership'),
    path('run-events/', views.run_events, name='run_events'),
    path('run-events/<int:event_id>/', views.run_event_detail, name='run_event_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-runs/', views.my_runs, name='my_runs'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]