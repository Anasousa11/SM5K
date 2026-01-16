from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class MemberProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile"
    )
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    PACE_CHOICES = [
        ("slow", "Slow (7+ min/km)"),
        ("medium", "Medium (5–7 min/km)"),
        ("fast", "Fast (<5 min/km)"),
    ]
    pace = models.CharField(
        max_length=10,
        choices=PACE_CHOICES,
        default="slow"
    )

    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner"
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} profile"

    @property
    def active_membership(self):
        today = timezone.now().date()
        return (
            self.memberships
            .filter(status="active", end_date__gte=today)
            .order_by("-end_date")
            .first()
        )

    @property
    def has_active_membership(self):
        return self.active_membership is not None
        

class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    max_sessions_per_week = models.PositiveIntegerField(
        default=0,
        help_text="0 means unlimited sessions per week."
    )

    def __str__(self):
        return self.name


class Membership(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name="memberships"
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active"
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


class RunEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    distance_km = models.DecimalField(max_digits=4, decimal_places=1)
    meeting_location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=20)

    PACE_GROUP_CHOICES = [
        ("slow", "Slow"),
        ("medium", "Medium"),
        ("fast", "Fast"),
        ("mixed", "Mixed"),
    ]
    pace_group = models.CharField(
        max_length=10,
        choices=PACE_GROUP_CHOICES,
        default="mixed"
    )

    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} - {self.date}"

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


class RunRegistration(models.Model):
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="run_registrations"
    )
    event = models.ForeignKey(
        RunEvent,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="booked"
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    # Attendance / performance
    attended = models.BooleanField(default=False)
    finish_time_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional: whole minutes for finish time."
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-booked_at"]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
