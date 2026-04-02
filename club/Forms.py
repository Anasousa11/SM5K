from django import forms
from django.utils import timezone

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "location",
            "event_type",
            "distance_km",
            "target_reps",
            "capacity",
            "price_non_member",
            "price_member",
            "is_cancelled",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date < timezone.now().date():
            raise forms.ValidationError("Event date cannot be in the past.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        capacity = cleaned_data.get("capacity")
        price_member = cleaned_data.get("price_member")
        price_non_member = cleaned_data.get("price_non_member")

        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be later than start time.")

        if capacity is not None and capacity < 1:
            self.add_error("capacity", "Capacity must be at least 1.")

        if price_member is not None and price_member < 0:
            self.add_error("price_member", "Member price cannot be negative.")

        if price_non_member is not None and price_non_member < 0:
            self.add_error("price_non_member", "Non-member price cannot be negative.")

        return cleaned_data
