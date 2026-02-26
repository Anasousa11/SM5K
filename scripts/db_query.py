import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
django.setup()

from club.models import Event
from django.utils import timezone

print(f"Total events: {Event.objects.count()}")
print(f"Today's date: {timezone.now().date()}")
print("\nAll events:")
for e in Event.objects.all():
    print(f"  {e.id}: {e.title:30} trainer={e.trainer_id} cancelled={e.is_cancelled} date={e.date}")
