from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, Queue, QueueEntry
from .permissions import IsAdminUserRole
from .serializers import (
    AuditLogSerializer,
    PriorityUpdateSerializer,
    QueueEntrySerializer,
    QueueJoinSerializer,
    QueueSerializer,
)
from .services import call_next_customer, join_queue, update_priority


class QueueListCreateView(generics.ListCreateAPIView):
    queryset = Queue.objects.all().order_by("-created_at")
    serializer_class = QueueSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QueueDetailView(generics.RetrieveUpdateAPIView):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer


class JoinQueueView(APIView):
    def post(self, request, queue_id):
        serializer = QueueJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            queue = Queue.objects.get(id=queue_id)
            entry = join_queue(
                queue=queue,
                user=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except Queue.DoesNotExist:
            return Response(
                {"detail": "Queue not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            QueueEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class QueueStatusView(APIView):
    def get(self, request, queue_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return Response(
                {"detail": "Queue not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        currently_serving = (
            QueueEntry.objects.filter(queue=queue, status="called")
            .order_by("-called_at")
            .first()
        )

        waiting_count = QueueEntry.objects.filter(
            queue=queue,
            status="waiting",
        ).count()

        return Response(
            {
                "queue_id": str(queue.id),
                "queue_name": queue.name,
                "status": queue.status,
                "waiting_count": waiting_count,
                "currently_serving": (
                    QueueEntrySerializer(currently_serving).data
                    if currently_serving
                    else None
                ),
            }
        )


class EntryDetailView(generics.RetrieveAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer


class CancelEntryView(APIView):
    def patch(self, request, entry_id):
        try:
            entry = QueueEntry.objects.get(id=entry_id, user=request.user)
        except QueueEntry.DoesNotExist:
            return Response(
                {"detail": "Queue entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if entry.status != "waiting":
            return Response(
                {"detail": "Only waiting entries can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry.status = "cancelled"
        entry.save(update_fields=["status"])

        return Response(QueueEntrySerializer(entry).data)


class CallNextCustomerView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, queue_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return Response(
                {"detail": "Queue not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        entry = call_next_customer(queue=queue, actor=request.user)

        if not entry:
            return Response(
                {"detail": "No waiting customers in this queue."},
                status=status.HTTP_404_NOT_FOUND,
            )

        remaining_waiting = QueueEntry.objects.filter(
            queue=queue,
            status="waiting",
        ).count()

        return Response(
            {
                "called_entry": QueueEntrySerializer(entry).data,
                "remaining_waiting": remaining_waiting,
            }
        )


class UpdatePriorityView(APIView):
    permission_classes = [IsAdminUserRole]

    def patch(self, request, entry_id):
        serializer = PriorityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            entry = QueueEntry.objects.get(id=entry_id)
        except QueueEntry.DoesNotExist:
            return Response(
                {"detail": "Queue entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        entry = update_priority(
            entry=entry,
            actor=request.user,
            priority_level=serializer.validated_data["priority_level"],
            reason=serializer.validated_data["reason"],
        )

        return Response(
            {
                "entry_id": str(entry.id),
                "priority_level": entry.priority_level,
                "status": entry.status,
                "updated_position": entry.position,
            }
        )


class QueueAuditLogView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        queue_id = self.kwargs["queue_id"]
        return AuditLog.objects.filter(
            metadata__queue_id=str(queue_id)
        ).order_by("-created_at")