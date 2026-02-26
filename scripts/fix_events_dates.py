#!/usr/bin/env python
import os
import sys
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from club.models import Event, TrainerProfile
from django.utils import timezone
from django.contrib.auth.models import User

# Ensure trainer exists
trainer_user, _ = User.objects.get_or_create(
    username='trainer',
    defaults={'first_name': 'Main', 'last_name': 'Trainer'}
)
trainer, _ = TrainerProfile.objects.get_or_create(
    user=trainer_user,
    defaults={'display_name': 'Main Trainer'}
)

# Get tomorrow and next 7 days
tomorrow = timezone.now().date() + timedelta(days=1)
next_week = tomorrow + timedelta(days=7)

# Update existing events with future dates
events_to_update = [
    ('SM5K', tomorrow),
    ('Push up Challenge', tomorrow + timedelta(days=1)),
    ('Burpees Challenge', tomorrow + timedelta(days=2)),
    ('SM10K', tomorrow + timedelta(days=3)),
]

for title, new_date in events_to_update:
    event = Event.objects.filter(title=title, trainer=trainer).first()
    if event:
        event.date = new_date
        event.is_cancelled = False
        event.save()
        print(f"Updated: {title} -> {new_date}")
    else:
        print(f"Not found: {title}")

# Create new events if theydon't exist
new_events = [
    ('Running Club', 'running_club', tomorrow + timedelta(days=4), 5.0, None),
    ('1000 Burpees Challenge', 'challenge', tomorrow + timedelta(days=5), None, 1000),
    ('Club Press Up Challenge', 'challenge', tomorrow + timedelta(days=6), None, 500),
    ('Morning Fitness Class', 'class', next_week, None, None),
]

for title, event_type, date, distance, reps in new_events:
    event, created = Event.objects.get_or_create(
        title=title,
        trainer=trainer,
        defaults={
            'date': date,
            'start_time': timezone.now().time(),
            'capacity': 20,
            'event_type': event_type,
            'distance_km': distance,
            'target_reps': reps,
            'description': f'{title}: Upcoming event',
            'is_cancelled': False,
        }
    )
    status = 'created' if created else 'exists'
    print(f'{status}: {title} on {date}')

print(f'\nTotal events (future): {Event.objects.filter(date__gte=timezone.now().date(), is_cancelled=False).count()}')
