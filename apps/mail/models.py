from django.db import models

from apps.base.models import Base


class EmailTemplate(Base):
    key_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    template = models.TextField(blank=True)
