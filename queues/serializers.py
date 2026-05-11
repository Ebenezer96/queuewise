from rest_framework import serializers

from .models import AuditLog, Notification, Queue, QueueEntry


class QueueSerializer(serializers.ModelSerializer):

    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Queue
        fields = [
            "id",
            "name",
            "description",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]


class QueueEntrySerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)
    queue = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QueueEntry
        fields = [
            "id",
            "queue",
            "user",
            "position",
            "priority_level",
            "reason",
            "status",
            "joined_at",
            "called_at",
            "served_at",
        ]
        read_only_fields = [
            "id",
            "position",
            "priority_level",
            "status",
            "joined_at",
            "called_at",
            "served_at",
        ]


class QueueJoinSerializer(serializers.Serializer):

    reason = serializers.CharField(required=False)


class PriorityUpdateSerializer(serializers.Serializer):

    priority_level = serializers.IntegerField(min_value=0)
    reason = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):

    actor = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = "__all__"