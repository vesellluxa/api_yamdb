from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator


class YamDBUser(AbstractUser):
    ROLES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    ]

    role = models.CharField(max_length=100, choices=ROLES, default='user')
    bio = models.CharField(max_length=100, null=True, blank=True)

    def send_confirmation_code(self):
        subject = 'Email Verification'
        verification_token = default_token_generator.make_token(self)
        send_mail(
            subject=subject,
            message=f'your confirmation code is {verification_token}',
            from_email='yamdbservice@gmail.com',
            recipient_list=[self.email]
        )
