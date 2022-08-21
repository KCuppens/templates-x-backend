from django.db import models


class ConfigManager(models.Manager):
    def get_config(self, key_name: str) -> str:
        qs = self.filter(key_name=key_name).first()
        if qs:
            return str(qs.value) if qs.value else ""
        return ''