#!/usr/bin/env python
"""Create a test user for login testing."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

# Create/update test user
user, created = User.objects.get_or_create(
    username='testuser123',
    defaults={'email': 'testuser@example.com'}
)

if created or not user.has_usable_password():
    user.set_password('TestPass123!')
    user.save()
    status = "Created" if created else "Updated"
    print(f"{status} user: {user.username}")
else:
    print(f"User already exists: {user.username}")

# Ensure EmailAddress record exists and is verified
email, created = EmailAddress.objects.get_or_create(
    user=user,
    email=user.email,
    defaults={'verified': True, 'primary': True}
)

print(f"Email: {user.email}")
print(f"Email verified: {email.verified}")
print(f"\n✓ Test user ready!")
print(f"  Username: testuser123")
print(f"  Password: TestPass123!")
print(f"  Email: {user.email}")
