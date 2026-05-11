from django.urls import path

from .views import (
    CallNextCustomerView,
    CancelEntryView,
    EntryDetailView,
    JoinQueueView,
    QueueAuditLogView,
    QueueDetailView,
    QueueListCreateView,
    QueueStatusView,
    UpdatePriorityView,
)

urlpatterns = [
    path("queues/", QueueListCreateView.as_view(), name="queue-list-create"),
    path("queues/<uuid:pk>/", QueueDetailView.as_view(), name="queue-detail"),
    path("queues/<uuid:queue_id>/join/", JoinQueueView.as_view(), name="queue-join"),
    path("queues/<uuid:queue_id>/status/", QueueStatusView.as_view(), name="queue-status"),
    path("queues/<uuid:queue_id>/call-next/", CallNextCustomerView.as_view(), name="queue-call-next"),
    path("queues/<uuid:queue_id>/audit-logs/", QueueAuditLogView.as_view(), name="queue-audit-logs"),

    path("entries/<uuid:pk>/", EntryDetailView.as_view(), name="entry-detail"),
    path("entries/<uuid:entry_id>/cancel/", CancelEntryView.as_view(), name="entry-cancel"),
    path("entries/<uuid:entry_id>/priority/", UpdatePriorityView.as_view(), name="entry-priority"),
]