from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import models

from apps.base.models import Base

User = get_user_model()


class Company(Base):
    # Company administrator
    administrator = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True
    )
    # All invited users
    invited_users = models.ManyToManyField(
        User, related_name="invited_users", blank=True
    )
    # Company name
    name = models.CharField(max_length=255)
    # Company site url
    site = models.URLField(max_length=255, null=True, blank=True)


Group.add_to_class(
    "company",
    models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_group_permissions",
        null=True,
        blank=True
    ),
)
Permission.add_to_class(
    "company",
    models.ManyToManyField(
        Company, related_name="company_permission_group", blank=True
    ),
)
