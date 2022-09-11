import apps.data.constants as C
from django.db import models

from apps.base.models import Base
from apps.company.models import Company


class Storage(Base):
    is_selected = models.BooleanField(default=False)
    storage_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=C.STORAGE_TYPES,
        default=C.STORAGE_TYPE_AWS,
    )

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=True, null=True
    )

    # Google storage
    auth_file = models.FileField(
        upload_to="storage/google/",
        blank=True, null=True
    )
    project_id = models.CharField(max_length=255, blank=True, null=True)

    # AWS S3
    access_key = models.CharField(max_length=255, blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    bucket_name = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.storage_type
