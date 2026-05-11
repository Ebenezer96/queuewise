# RFC: Priority Queue & Notification Engine for QueueWise

## 1. Problem Statement

Many organizations still manage queues manually or with basic first-come-first-served systems. This creates poor customer experience because users do not know their current position, staff cannot easily prioritize urgent cases, and customers may miss their turn without timely updates.

For businesses such as clinics, banks, salons, and service centers, queues are not always simple. Some customers may require urgent attention, some may cancel, and staff need a reliable way to call the next person without losing track of queue history.

QueueWise needs a backend feature that can manage queue entries, calculate queue position, support priority changes, and notify users when they are close to being served.

---

## 2. Proposed Solution

Build a **Priority Queue & Notification Engine**.

The system will allow customers to join a queue and receive a queue entry. Admin users can call the next customer, pause or resume queues, and adjust customer priority when needed. The backend will maintain queue order using position and priority level.

The system will also create notification records when users are near their turn. A background worker will process pending notifications separately from the main API request cycle.

### High-Level Flow

```text
Customer joins queue
        ↓
Backend creates queue entry
        ↓
System calculates position
        ↓
Admin calls next customer
        ↓
Queue positions are updated
        ↓
Notification job alerts nearby customers
```

---

## 3. Cross-Track Impact

### Frontend

Frontend will need screens for:

* customer queue joining
* live queue status
* admin queue management
* priority adjustment
* called/served/cancelled states

Frontend should expect queue entries to move across statuses such as:

* `waiting`
* `called`
* `served`
* `cancelled`

### Design

Design needs to define clear states for:

* waiting in queue
* near turn
* called
* missed/cancelled
* paused queue
* priority customer

### PM

PM needs to confirm:

* what counts as “near turn”
* whether priority should be manual only or automatic
* maximum queue size
* whether notifications are email-only for MVP
* whether customers can join multiple queues at once

---

## 4. Alternatives Considered

### Alternative 1: Simple FIFO Queue

This would serve customers strictly by arrival time.

Rejected because it does not support urgent cases, VIP handling, or operational flexibility. It is simpler but not realistic for service environments where staff may need to prioritize some users.

### Alternative 2: WebSocket-Based Real-Time Queue Updates

This would push queue changes instantly to connected clients.

Rejected for MVP because it adds infrastructure and deployment complexity. Polling the queue status endpoint is simpler, easier to test, and good enough for the first version.

### Alternative 3: Process Notifications Inside API Requests

This would send notifications immediately during queue actions.

Rejected because notification delivery can fail or become slow. Keeping notification work in a background worker prevents API requests from being blocked.

---

## 5. API Contract

### Create Queue

```http
POST /api/v1/queues
```

### Request

```json
{
  "name": "Main Clinic Queue",
  "description": "General outpatient queue"
}
```

### Response

```json
{
  "id": "uuid",
  "name": "Main Clinic Queue",
  "status": "active",
  "created_at": "2026-05-11T10:00:00Z"
}
```

---

### Join Queue

```http
POST /api/v1/queues/{queue_id}/join
```

### Request

```json
{
  "reason": "General consultation"
}
```

### Response

```json
{
  "entry_id": "uuid",
  "queue_id": "uuid",
  "status": "waiting",
  "position": 5,
  "priority_level": 0,
  "joined_at": "2026-05-11T10:05:00Z"
}
```

---

### Get Queue Status

```http
GET /api/v1/queues/{queue_id}/status
```

### Response

```json
{
  "queue_id": "uuid",
  "queue_name": "Main Clinic Queue",
  "status": "active",
  "waiting_count": 8,
  "currently_serving": {
    "entry_id": "uuid",
    "position": 1,
    "status": "called"
  }
}
```

---

### Get Entry Status

```http
GET /api/v1/entries/{entry_id}
```

### Response

```json
{
  "entry_id": "uuid",
  "queue_id": "uuid",
  "status": "waiting",
  "position": 3,
  "priority_level": 0,
  "estimated_wait_minutes": 15
}
```

---

### Call Next Customer

```http
POST /api/v1/queues/{queue_id}/call-next
```

### Response

```json
{
  "called_entry": {
    "entry_id": "uuid",
    "status": "called",
    "called_at": "2026-05-11T10:20:00Z"
  },
  "remaining_waiting": 7
}
```

---

### Update Priority

```http
PATCH /api/v1/entries/{entry_id}/priority
```

### Request

```json
{
  "priority_level": 2,
  "reason": "Urgent medical case"
}
```

### Response

```json
{
  "entry_id": "uuid",
  "priority_level": 2,
  "status": "waiting",
  "updated_position": 1
}
```

---

## 6. Risks and Open Questions

### Risks

* Queue position may become incorrect if multiple admins call customers at the same time.
* Notification delivery may fail if the email service is unavailable.
* Priority changes can feel unfair if not properly audited.
* Large queues may require optimization for position recalculation.
* Users may abuse joining/cancelling if no limits are added.

### Open Questions

* Should one user be allowed to join more than one queue?
* Should notifications be sent by email only for MVP?
* Should admins be allowed to manually mark users as served?
* What priority levels should exist?
* Should the system auto-cancel a user if they do not respond after being called?

---

## 7. Definition of Done

This feature is complete when:

* Customers can join an active queue.
* The backend assigns a queue position.
* Customers can view their queue entry status.
* Admins can call the next customer.
* Admins can update customer priority.
* Queue ordering respects priority before normal arrival order.
* Notification records are created when users are close to their turn.
* A background worker processes pending notifications.
* All queue-changing admin actions are recorded in audit logs.
* Tests cover queue joining, call-next logic, priority changes, and authorization.
* Existing endpoints remain unaffected.
* System design document and architecture diagram are completed.
