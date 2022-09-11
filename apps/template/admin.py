from django.contrib import admin

from apps.template.models import Template, TemplateCategory

admin.site.register(Template)
admin.site.register(TemplateCategory)
