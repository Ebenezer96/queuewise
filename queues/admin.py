from django.contrib import admin

from .models import AuditLog, Notification, Queue, QueueEntry


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description")


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    list_display = (
        "queue",
        "user",
        "position",
        "priority_level",
        "status",
        "joined_at",
    )
    list_filter = ("status", "priority_level", "joined_at")
    search_fields = ("queue__name", "user__username", "reason")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "queue_entry", "status", "retry_count", "created_at", "sent_at")
    list_filter = ("status", "created_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "entity_type", "entity_id", "created_at")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("action", "entity_type")
