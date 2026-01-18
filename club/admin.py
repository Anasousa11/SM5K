from django.contrib import admin
from .models import (
    TrainerProfile,
    ClientProfile,
    MembershipPlan,
    Membership,
    Event,
    EventRegistration,
)


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'access_type', 'is_active')
    list_filter = ('access_type', 'is_active')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'status')
    list_filter = ('plan', 'status')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'start_time', 'location', 'capacity', 'is_cancelled')
    list_filter = ('event_type', 'date', 'is_cancelled')
    search_fields = ('title', 'location')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'booked_at')
    list_filter = ('event', 'status')


admin.site.register(TrainerProfile)
admin.site.register(ClientProfile)
