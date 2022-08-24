from django.db import models

from apps.base.models import Base


class Contact(Base):
    question = models.CharField(max_length=255)
    message = models.TextField()
    email = models.EmailField(max_length=100)
