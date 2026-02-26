from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ClientProfile

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        # create a linked profile but do not break the request if something goes wrong
        try:
            ClientProfile.objects.create(user=instance)
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Failed to create ClientProfile for user %s", instance
            )