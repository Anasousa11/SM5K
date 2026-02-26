import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from club.models import Event
from django.utils import timezone

all_events = Event.objects.all()
print(f'Total events: {all_events.count()}')
for e in all_events:
    print(f'  - {e.title} (type: {e.event_type}, date: {e.date}, trainer: {e.trainer})')

print('\nFuture non-cancelled events:')
future = Event.objects.filter(date__gte=timezone.now().date(), is_cancelled=False)
print(f'Count: {future.count()}')
for e in future:
    print(f'  - {e.title}')
