from django.db import transaction
from django.utils import timezone

from .models import AuditLog, Notification, QueueEntry


def create_audit_log(actor, action, entity_type, entity_id, metadata=None):
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )


@transaction.atomic
def join_queue(queue, user, reason=""):
    if queue.status != "active":
        raise ValueError("Cannot join a queue that is not active.")

    existing_entry = QueueEntry.objects.filter(
        queue=queue,
        user=user,
        status="waiting",
    ).first()

    if existing_entry:
        return existing_entry

    last_position = (
        QueueEntry.objects.filter(queue=queue)
        .order_by("-position")
        .values_list("position", flat=True)
        .first()
    )

    next_position = (last_position or 0) + 1

    entry = QueueEntry.objects.create(
        queue=queue,
        user=user,
        position=next_position,
        reason=reason,
    )

    create_audit_log(
        actor=user,
        action="JOIN_QUEUE",
        entity_type="QueueEntry",
        entity_id=entry.id,
        metadata={
            "queue_id": str(queue.id),
            "position": entry.position,
        },
    )

    return entry


@transaction.atomic
def call_next_customer(queue, actor):
    next_entry = (
        QueueEntry.objects.select_for_update()
        .filter(queue=queue, status="waiting")
        .order_by("-priority_level", "position", "joined_at")
        .first()
    )

    if not next_entry:
        return None

    next_entry.status = "called"
    next_entry.called_at = timezone.now()
    next_entry.save(update_fields=["status", "called_at"])

    create_audit_log(
        actor=actor,
        action="CALL_NEXT_CUSTOMER",
        entity_type="QueueEntry",
        entity_id=next_entry.id,
        metadata={
            "queue_id": str(queue.id),
            "priority_level": next_entry.priority_level,
        },
    )

    create_near_turn_notifications(queue)

    return next_entry


@transaction.atomic
def update_priority(entry, actor, priority_level, reason):
    old_priority = entry.priority_level

    entry.priority_level = priority_level
    entry.save(update_fields=["priority_level"])

    create_audit_log(
        actor=actor,
        action="UPDATE_PRIORITY",
        entity_type="QueueEntry",
        entity_id=entry.id,
        metadata={
            "old_priority": old_priority,
            "new_priority": priority_level,
            "reason": reason,
        },
    )

    return entry


def create_near_turn_notifications(queue):
    nearby_entries = (
        QueueEntry.objects.filter(queue=queue, status="waiting")
        .order_by("-priority_level", "position", "joined_at")[:3]
    )

    for entry in nearby_entries:
        Notification.objects.get_or_create(
            user=entry.user,
            queue_entry=entry,
            status="pending",
            defaults={
                "message": "You are close to being served. Please stay available.",
            },
        )