import uuid

from django.db import models
from django.utils import timezone

now = timezone.now()
from apps.company.models import Company
from django.contrib.auth.models import Group,Permission
Group.add_to_class('company',models.ForeignKey(Company,on_delete=models.CASCADE,related_name='company_group',default=0))
Permission.add_to_class('company',models.ManyToManyField(Company,related_name="company_permission"))

# $ standard base model being used in every object
class Base(models.Model):
    STATE_DRAFT = "draft"
    STATE_IN_REVIEW = "in review"
    STATE_PUBLISHED = "published"
    STATE_CHANGES_REQUESTED = "changes requested"
    STATE_SCHEDULE = "schedule"

    STATES = [
        (STATE_DRAFT, "Draft"),
        (STATE_IN_REVIEW, "In review"),
        (STATE_PUBLISHED, "Published"),
        (STATE_CHANGES_REQUESTED, "Changes requested"),
        (STATE_SCHEDULE, "Schedule"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Unique identification",
    )
    date_created = models.DateTimeField(auto_now=True, verbose_name="Date of creation")
    date_published = models.DateTimeField(
        default=timezone.now, blank=True, null=True, verbose_name="Publishingdate"
    )
    date_expired = models.DateTimeField(
        blank=True, null=True, verbose_name="Expiring date"
    )
    date_updated = models.DateTimeField(
        auto_now=True, verbose_name="Date of last update"
    )
    date_deleted = models.DateTimeField(
        null=True, blank=True, verbose_name="Delete date"
    )
    state = models.CharField(max_length=255, choices=STATES, default=STATE_DRAFT)

    def __str__(self):
        return str(self.date_published)

    class Meta:
        abstract = True
