from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def createUpdated(sender, instance, created, **kwargs):


    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=user.first_name,

        )
        subject = 'Welcome to developerSquad'
        message = f'Hi {user.first_name}\n' \
                  f'We are glad you are here.\n' \
                  f'your username is "{user.username}"\n' \
                  f'Please complete your Profile in our website https://developersquad.herokuapp.com/" '
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Profile)
def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.name
        user.email = profile.email
        user.username = profile.username
        user.save()


@receiver(post_delete, sender=Profile)
def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass
        
    

