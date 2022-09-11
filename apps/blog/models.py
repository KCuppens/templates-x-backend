from django.db import models

from apps.base.models import Base


class Blog(Base):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="blog/")
    keywords = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blog"
