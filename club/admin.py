from django.contrib import admin
from .models import (
    TrainerProfile,
    ClientProfile,
    MembershipPlan,
    Membership,
    Event,
    EventRegistration,
)

admin.site.register(TrainerProfile)
admin.site.register(ClientProfile)
admin.site.register(MembershipPlan)
admin.site.register(Membership)
admin.site.register(Event)
admin.site.register(EventRegistration)
