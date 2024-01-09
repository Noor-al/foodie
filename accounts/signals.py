from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            # incase the user get updated we will update the profile also  
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # incase we are updating the user but there was no profile for the user
            UserProfile.objects.create(user=instance)


# connecting sener and receiver
# post_save.connect(post_save_create_profile_receiver, sender=User)
# another way is the decorators @receiver