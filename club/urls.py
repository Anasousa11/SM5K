from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('membership-plans/', views.membership_plans, name='membership_plans'),
    path('activate-membership/<int:plan_id>/', views.activate_membership, name='activate_membership'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-events/', views.my_events, name='my_events'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('trainer/dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
]