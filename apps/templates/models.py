from django.db import models
from apps.base.models import Base


class TemplateCategory(Base):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Template Category'
        verbose_name_plural = 'Template Categories'


class Template(Base):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    summary = models.TextField(blank=True)
    screenshot = models.CharField(max_length=255,blank=True)
    content_html = models.TextField(blank=True)
    content_json = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name