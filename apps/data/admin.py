from django.contrib import admin

from apps.data.models import ConvertAction


class ConvertActionAdmin(admin.ModelAdmin):
    list_display = ("from_action", "to_action", "to_action_type")


# Register your models here.
admin.site.register(ConvertAction, ConvertActionAdmin)
