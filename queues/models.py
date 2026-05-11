from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Queue(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("closed", "Closed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_queues",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class QueueEntry(models.Model):

    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("called", "Called"),
        ("served", "Served"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    queue = models.ForeignKey(
        Queue,
        on_delete=models.CASCADE,
        related_name="entries",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="queue_entries",
    )

    position = models.PositiveIntegerField()

    priority_level = models.PositiveIntegerField(default=0)

    reason = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting",
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    called_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    served_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-priority_level",
            "position",
            "joined_at",
        ]

    def __str__(self):
        return f"{self.user} - {self.queue}"


class Notification(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    queue_entry = models.ForeignKey(
        QueueEntry,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    retry_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Notification for {self.user}"


class AuditLog(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=255)

    entity_type = models.CharField(max_length=100)

    entity_id = models.UUIDField()

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} - {self.action}"