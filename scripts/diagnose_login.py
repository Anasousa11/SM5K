#!/usr/bin/env python
"""Diagnostic script to inspect login configuration and users on Heroku."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinmancha.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

print("=" * 60)
print("AUTHENTICATION SETTINGS")
print("=" * 60)
print(f"DEBUG: {settings.DEBUG}")
print(f"ACCOUNT_AUTHENTICATION_METHOD: {settings.ACCOUNT_AUTHENTICATION_METHOD}")
print(f"ACCOUNT_EMAIL_REQUIRED: {settings.ACCOUNT_EMAIL_REQUIRED}")
print(f"ACCOUNT_EMAIL_VERIFICATION: {settings.ACCOUNT_EMAIL_VERIFICATION}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

print("\n" + "=" * 60)
print("DATABASE USERS AND EMAIL VERIFICATION STATUS")
print("=" * 60)
users = User.objects.all()
print(f"Total users: {users.count()}\n")

for user in users.order_by('-date_joined'):
    emails = EmailAddress.objects.filter(user=user)
    if emails.exists():
        email_list = [(e.email, e.verified, e.primary) for e in emails]
        print(f"User: {user.username}")
        print(f"  Email (primary): {user.email}")
        print(f"  Created: {user.date_joined}")
        print(f"  EmailAddress records: {email_list}")
    else:
        print(f"User: {user.username}")
        print(f"  Email (primary): {user.email}")
        print(f"  Created: {user.date_joined}")
        print(f"  EmailAddress records: NONE (this may be the problem!)")
    print()

print("=" * 60)
print("DIAGNOSIS")
print("=" * 60)
unverified = EmailAddress.objects.filter(verified=False).count()
no_email_record = User.objects.exclude(emailaddress__isnull=False).count()

if unverified > 0:
    print(f"⚠ WARNING: {unverified} users have unverified email addresses.")
    if settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory":
        print("  → ACCOUNT_EMAIL_VERIFICATION='mandatory' means users MUST verify email to login!")
        
if no_email_record > 0:
    print(f"⚠ WARNING: {no_email_record} users have NO EmailAddress record!")
    print("  → These users cannot login with allauth!")

if settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory":
    print("\n✗ PROBLEM FOUND: ACCOUNT_EMAIL_VERIFICATION is 'mandatory'")
    print("  All users must verify their email to login.")
    print("  SOLUTION: Change to 'optional' in settings.py or send verification emails.")
