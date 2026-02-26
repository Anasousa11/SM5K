#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from club.models import TrainerProfile, Event
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

# Get or create a trainer
trainer_user, created = User.objects.get_or_create(
    username='trainer',
    defaults={'first_name': 'Main', 'last_name': 'Trainer'}
)
trainer, created = TrainerProfile.objects.get_or_create(
    user=trainer_user,
    defaults={'display_name': 'Main Trainer'}
)

# Create events
events_to_create = [
    {
        'title': 'Running Club',
        'event_type': 'running_club',
        'distance_km': 5.0,
        'description': 'Weekly running club session',
    },
    {
        'title': '1000 Burpees Challenge',
        'event_type': 'challenge',
        'target_reps': 1000,
        'description': 'Can you complete 1000 burpees?',
    },
    {
        'title': 'Club Press Up Challenge',
        'event_type': 'challenge',
        'target_reps': 500,
        'description': 'Push-up challenge for club members',
    },
    {
        'title': 'Morning Fitness Class',
        'event_type': 'class',
        'description': 'Full body fitness class',
    },
]

tomorrow = timezone.now().date() + datetime.timedelta(days=1)
for event_data in events_to_create:
    event, created = Event.objects.get_or_create(
        title=event_data['title'],
        trainer=trainer,
        defaults={
            'date': tomorrow,
            'start_time': timezone.now().time(),
            'capacity': 20,
            'event_type': event_data['event_type'],
            'distance_km': event_data.get('distance_km'),
            'target_reps': event_data.get('target_reps'),
            'description': event_data['description'],
            'is_cancelled': False,
        }
    )
    status = 'created' if created else 'exists'
    print(f'{status}: {event.title}')

events = Event.objects.all()
print(f'\nTotal events: {events.count()}')
for e in events:
    print(f'  - {e.title} ({e.event_type})')
