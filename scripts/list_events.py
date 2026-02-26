#!/usr/bin/env python
"""Simple script to list all events in the database."""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
django.setup()

from club.models import Event
from django.utils import timezone

try:
    events = list(Event.objects.all().values('id', 'title', 'date', 'trainer_id', 'is_cancelled'))
    print(f"TOTAL_EVENTS:{len(events)}")
    for e in events:
        print(f"EVENT:{e['id']}:{e['title']}:{e['date']}:{e['trainer_id']}:{e['is_cancelled']}")
except Exception as ex:
    print(f"ERROR:{ex}")
