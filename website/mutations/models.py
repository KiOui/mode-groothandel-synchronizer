from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import ForeignKey, PositiveIntegerField


class Mutation(models.Model):
    METHOD_CREATE = 0
    METHOD_UPDATE = 1
    METHOD_DELETE = 2
    TYPES = ((METHOD_CREATE, "Create"), (METHOD_UPDATE, "Update"), (METHOD_DELETE, "Delete"))

    TRIGGER_WEBHOOK = 0
    TRIGGER_MANUAL = 1

    TRIGGERS = ((TRIGGER_WEBHOOK, "Webhook"), (TRIGGER_MANUAL, "Manual"))

    created = models.DateTimeField(auto_now_add=True)
    method = models.PositiveIntegerField(choices=TYPES)
    trigger = models.PositiveIntegerField(choices=TRIGGERS)
    content_type = ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = PositiveIntegerField()
    on = GenericForeignKey("content_type", "object_id")
    success = models.BooleanField()
