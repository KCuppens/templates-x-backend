from django.db import models

import apps.data.constants as C
from apps.base.models import Base


class ConvertAction(Base):
    from_action = models.CharField(max_length=255, null=True)
    to_action = models.CharField(max_length=255, null=True)
    to_action_type = models.CharField(
        max_length=255, choices=C.MEDIA_TYPES, default=C.MEDIA_TYPE_DOCUMENT
    )
