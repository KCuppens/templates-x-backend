from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Company(models.Model):
    # Company administrator
    administrator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # All invited users
    invited_users = models.ManyToManyField(User, related_name='invited_users', blank=True)
    # Company name
    name = models.CharField(max_length=255)
    # Company site url
    site = models.URLField(max_length=255, null=True, blank=True)

