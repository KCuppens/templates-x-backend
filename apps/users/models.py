from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import uuid
from apps.users.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.company.models import Company


class User(AbstractUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_administrator = models.BooleanField(default=False)
    # Active company
    active_company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_activation_link(self):
        token = account_activation_token.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        return f"/activation/{uid}/{token}"
    
    def get_password_reset_link(self):
        token = account_activation_token.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        return f"/reset-password/{uid}/{token}"
