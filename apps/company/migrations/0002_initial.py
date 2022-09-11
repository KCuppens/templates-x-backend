# Generated by Django 4.1 on 2022-08-30 20:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("company", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="administrator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="invited_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="invited_users",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
