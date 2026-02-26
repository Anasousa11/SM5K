import os
import sys
# ensure project root on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sinmancha.settings')
import django

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from club.models import TrainerProfile, Event
import datetime
from django.conf import settings

# mimic production
settings.DEBUG = False
settings.ALLOWED_HOSTS = ['localhost','127.0.0.1','*']

# create data
trainer_user = User.objects.create_user(username='t', password='p')
trainer = TrainerProfile.objects.create(user=trainer_user)
event = Event.objects.create(title='Test', date=datetime.date.today()+datetime.timedelta(days=1), start_time=datetime.time(10,0), capacity=5, trainer=trainer)

c = Client()
print('anon status', c.get(reverse('events'), HTTP_HOST='example.com').status_code)

user = User.objects.create_user(username='u', password='p')
c.login(username='u', password='p')
resp = c.get(reverse('events'), HTTP_HOST='example.com')
print('auth status', resp.status_code)
print('body snippet', resp.content[:300])
