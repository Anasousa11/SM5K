from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    specialties = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. running, strength, conditioning"
    )
    instagram_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    def __str__(self):
        return self.display_name or self.user.get_full_name() or self.user.username


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone
