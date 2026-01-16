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
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner",
    )

    primary_trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="clients",
        help_text="The trainer this client works with.",
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (client)"

    @property
    def active_membership(self):
        """Return the most recent active membership (if any)."""
        today = timezone.now().date()
        return (
            self.user.client_memberships
            .filter(status="active", end_date__gte=today)
            .order_by("-end_date")
            .first()
        )

    @property
    def has_active_membership(self):
        return self.active_membership is not None


class MembershipPlan(models.Model):
    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="plans",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)

    ACCESS_TYPE_CHOICES = [
        ("sessions", "Limited sessions per week"),
        ("unlimited", "Unlimited sessions"),
    ]
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        default="unlimited",
    )
    max_sessions_per_week = models.PositiveIntegerField(
        default=0,
        help_text="Used only if access type is 'sessions'. 0 means unlimited."
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["trainer", "name"]

    def __str__(self):
        return f"{self.name} ({self.trainer})"


class Membership(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_memberships",
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
    )
    auto_renew = models.BooleanField(default=False)

    class Meta:
        ordering = ["-end_date"]

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == "active" and self.end_date and self.end_date >= today


class Event(models.Model):
    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True)

    EVENT_TYPE_CHOICES = [
        ("running_club", "Running club"),
        ("class", "Class / session"),
        ("challenge", "Challenge (e.g. 1000 burpees)"),
    ]
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default="class",
    )

    distance_km = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        help_text="Optional: for running events.",
    )
    target_reps = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional: for challenge events (e.g. 1000 burpees).",
    )

    capacity = models.PositiveIntegerField(default=20)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} - {self.date} ({self.trainer})"

    @property
    def is_past(self):
        today = timezone.now().date()
        return self.date < today

    @property
    def registrations_count(self):
        return self.registrations.filter(status="booked").count()

    @property
    def spots_left(self):
        return max(self.capacity - self.registrations_count, 0)

    @property
    def is_full(self):
        return self.spots_left <= 0


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="booked",
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    attended = models.BooleanField(default=False)
    performance_notes = models.TextField(
        blank=True,
        help_text="Optional notes e.g. completed 800/1000 burpees, PB time, etc."
    )

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-booked_at"]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
