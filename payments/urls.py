from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout/<int:plan_id>/", views.create_checkout_session, name="create_checkout"),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    path("webhook/", views.webhook, name="stripe_webhook"),
