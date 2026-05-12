# System Design: Priority Queue & Notification Engine

## 1. Overview

The Priority Queue & Notification Engine allows QueueWise to manage customer queues more intelligently than a basic first-come-first-served system.

Users can join a queue, receive a position, and track their status. Admins can call the next customer, adjust priority, and monitor queue progress. The backend is responsible for maintaining correct queue order, preserving queue history, and preparing notification records when users are close to being served.

## 2. Architecture

```
Client / Frontend
      |
      v
Django REST API
      |
      v
Queue Service Layer
      |
      v
Database
      |
      v
Notification Records
      |
      v
Background Worker / Notification Sender
````

## 3. Core Components

### Django REST API

Exposes endpoints for creating queues, joining queues, checking queue status, calling the next customer, and updating priority.

### Queue Service Layer

Handles business logic such as position assignment, queue ordering, priority updates, and state transitions.

### Database

Stores queues, queue entries, notification records, and audit logs.

### Notification Engine

Creates notification records when users are close to their turn. Notification delivery is handled separately from the main request cycle to avoid slowing down API responses.

## 4. Main Data Models

### Queue

Represents a service queue.

Key fields:

* id
* name
* description
* status
* created_by
* created_at
* updated_at

### QueueEntry

Represents a user’s place in a queue.

Key fields:

* id
* queue
* user
* position
* priority_level
* reason
* status
* joined_at
* called_at
* served_at

### AuditLog

Records important admin actions such as calling the next customer or changing priority.

Key fields:

* id
* action
* actor
* queue
* entry
* created_at

### Notification

Stores pending or processed notification events.

Key fields:

* id
* queue_entry
* notification_type
* status
* created_at
* processed_at

## 5. Request Lifecycle

### Join Queue Flow

```
User requests to join queue
        ↓
API validates active queue
        ↓
QueueEntry is created
        ↓
Position is calculated
        ↓
Response returns entry ID, position, and status
```

### Call Next Flow


Admin calls next customer
        ↓
API selects highest-priority waiting entry
        ↓
Entry status changes from waiting to called
        ↓
Queue positions are recalculated
        ↓
Audit log is created
        ↓
Nearby users may receive notification records
```

### Priority Update Flow

```text
Admin updates priority level
        ↓
API validates entry
        ↓
Priority level is updated
        ↓
Queue ordering is recalculated
        ↓
Audit log is created
        ↓
Updated position is returned
```

## 6. API Surface

| Method | Endpoint                             | Purpose                |
| ------ | ------------------------------------ | ---------------------- |
| POST   | /api/v1/queues/                      | Create a queue         |
| POST   | /api/v1/queues/{queue_id}/join/      | Join a queue           |
| GET    | /api/v1/queues/{queue_id}/status/    | Get queue status       |
| POST   | /api/v1/queues/{queue_id}/call-next/ | Call next customer     |
| GET    | /api/v1/entries/{entry_id}/          | Get queue entry status |
| PATCH  | /api/v1/entries/{entry_id}/priority/ | Update entry priority  |

## 7. Design Decisions

### Priority before arrival time

Queue ordering uses priority first, then join time. This allows urgent cases to move forward while still preserving fairness among users with the same priority level.

### Polling instead of WebSockets

The MVP uses REST endpoints and frontend polling instead of WebSockets. This reduces infrastructure complexity and is easier to test within the project timeline.

### Notification records instead of direct sending

Notifications are stored as records first and processed separately. This prevents slow or failed notification delivery from blocking queue actions.

### Audit logs for admin actions

Priority changes and call-next actions should be auditable because they affect fairness and user trust.

## 8. Risks and Mitigations

| Risk                                          | Mitigation                                                 |
| --------------------------------------------- | ---------------------------------------------------------- |
| Multiple admins call next at the same time    | Use database transactions around queue-changing operations |
| Priority changes feel unfair                  | Record priority updates in audit logs                      |
| Notification delivery fails                   | Store notification records and retry processing later      |
| Large queues make position recalculation slow | Add database indexes and optimize ordering queries         |
| Users miss their turn                         | Support called, served, cancelled, and missed states       |

## 9. Testing Strategy

The feature was tested locally using the Django REST Framework browsable API.

Tested flows:

* Queue creation
* Joining a queue
* Position assignment
* Queue status retrieval
* Call-next action
* Invalid queue ID handling
* Method validation for GET vs POST endpoints

## 10. Future Improvements

Future improvements include:

* WebSocket support for real-time queue updates
* Automatic missed-user handling
* Email or SMS notification delivery
* Queue analytics dashboard
* Stronger concurrency controls for high-traffic environments

```
