# Feature Specification: Bike CRUD API

**Feature Branch**: `001-bike-crud-api`
**Created**: 2026-03-24
**Status**: Draft
**Input**: User description: "I need to create a Flask API focused on providing full access to the CRUD operations of the Bike model, this model should have the following fields: ID, Brand, Type (Cross, Mountain, Street), Colour and state (Rented or Free). This Flask API should end up containarized inside a docker image and the database is going to be a MySQL engine. Take into account that this API is going to function as the Bike microservice in a large rental kubernetes service"

## Clarifications

### Session 2026-03-24

- Q: Should the frontend be restricted to read-only access, or should it have full CRUD access alongside internal services? → A: Full CRUD access for all consumers (FE and internal services alike). JWT-based auth is handled upstream and is out of scope for this spec.
- Q: Should the listing endpoint support filtering bikes by State and/or Type? → A: Filter by both State and Type (e.g., `?state=Free&type=Mountain`).
- Q: Should responses use a standard envelope wrapper or plain JSON? → A: Plain JSON — single bike as `{}`, list as `[]`, errors as `{"error": "..."}`.
- Q: How should the system handle simultaneous state updates to the same bike? → A: Concurrent conflict resolution is handled externally by an async message broker (RabbitMQ); out of scope for this microservice.
- Q: Where should CORS be handled? → A: At the API gateway / Kubernetes ingress; this microservice requires no CORS configuration.

### Session 2026-03-24 (amendment)

- Q: What type should the bike ID be? → A: UUID (system-generated, not an integer auto-increment).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a New Bike (Priority: P1)

An operator needs to add a new bike to the fleet by providing its brand, type, colour, and initial availability state. Once registered, the bike becomes visible and manageable within the rental system.

**Why this priority**: This is the foundation of the microservice — without the ability to create bikes, no other operation is possible. It unblocks all downstream rental workflows.

**Independent Test**: Can be fully tested by submitting a new bike record with valid fields and confirming it appears in subsequent listing requests with a system-assigned ID.

**Acceptance Scenarios**:

1. **Given** the bike inventory is empty, **When** an operator submits a new bike with brand "Trek", type "Mountain", colour "Red", and state "Free", **Then** the bike is stored and returned with a unique system-assigned ID.
2. **Given** a bike registration request is submitted with a missing mandatory field (e.g., no brand), **When** the request is processed, **Then** the system rejects it and returns a descriptive error message identifying the missing field.
3. **Given** a bike type outside the accepted values (Cross, Mountain, Street) is submitted, **When** the request is processed, **Then** the system rejects it with a clear validation error.

---

### User Story 2 - Retrieve Bike Information (Priority: P1)

An operator or another service in the rental platform needs to query individual bike details or list all bikes in the fleet to coordinate rentals and manage availability.

**Why this priority**: Read access is required by the rental orchestration service to check bike availability before assigning one to a customer. Without it, the wider platform cannot function.

**Independent Test**: Can be fully tested by first registering bikes and then querying them individually by ID and as a full list, confirming all stored fields are returned correctly.

**Acceptance Scenarios**:

1. **Given** a bike with a known ID exists, **When** an operator requests that bike by ID, **Then** all stored fields (ID, brand, type, colour, state) are returned accurately.
2. **Given** multiple bikes exist, **When** a full listing is requested with no filters, **Then** all bikes are returned with their complete details.
3. **Given** bikes of mixed states and types exist, **When** a listing is requested filtered by state "Free" and type "Mountain", **Then** only bikes matching both criteria are returned.
4. **Given** a request is made for a bike ID that does not exist, **When** the request is processed, **Then** the system responds with a clear "not found" indication and no partial data.

---

### User Story 3 - Update Bike Details or State (Priority: P2)

An operator needs to modify an existing bike's attributes — most commonly its state (transitioning between "Rented" and "Free") as part of the rental lifecycle, but also correcting other fields like colour or brand.

**Why this priority**: State updates are essential to the core rental loop. After P1 stories are in place, state management becomes the next critical need to support active rentals.

**Independent Test**: Can be fully tested by registering a bike, issuing an update to change its state from "Free" to "Rented", and confirming the change persists in subsequent reads.

**Acceptance Scenarios**:

1. **Given** a bike with state "Free" exists, **When** an operator updates its state to "Rented", **Then** the bike reflects the new state in all subsequent reads.
2. **Given** an update is submitted with an invalid state value (not "Rented" or "Free"), **When** the request is processed, **Then** the system rejects it with a validation error.
3. **Given** an update targets a bike ID that does not exist, **When** the request is processed, **Then** the system returns a "not found" indication without modifying any data.

---

### User Story 4 - Remove a Bike from the Fleet (Priority: P3)

An operator needs to permanently remove a bike record from the system — for example, when a bike is decommissioned, stolen, or retired from service.

**Why this priority**: Deletion is a lower-frequency operation and not blocking for the primary rental workflow. Core create/read/update flows deliver the most immediate business value.

**Independent Test**: Can be fully tested by registering a bike, deleting it by ID, and confirming it no longer appears in listing or individual read requests.

**Acceptance Scenarios**:

1. **Given** a bike with a known ID exists, **When** an operator deletes it by ID, **Then** the bike is removed from the system and no longer returned in any query.
2. **Given** a delete request targets a bike ID that does not exist, **When** the request is processed, **Then** the system returns a "not found" indication without affecting other records.

---

### Edge Cases

- Concurrent state updates (e.g., two requests marking the same bike as "Rented" simultaneously) are resolved externally by an async message broker; this microservice applies updates as received without conflict detection.
- How does the system handle requests with extra or unrecognised fields in the payload?
- What happens if the data store becomes temporarily unavailable — are errors surfaced clearly to the calling service?
- How are extremely long or special-character strings handled in fields like Brand or Colour?
- What happens if the service starts but cannot reach the data store on boot?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow creation of a bike record with the following mandatory fields: Brand, Type (one of: Cross, Mountain, Street), Colour, and State (one of: Rented, Free).
- **FR-002**: System MUST auto-assign a UUID as the unique identifier to each bike upon creation; callers MUST NOT provide the ID.
- **FR-003**: System MUST reject creation or update requests where Type is not one of the accepted values: Cross, Mountain, Street.
- **FR-004**: System MUST reject creation or update requests where State is not one of the accepted values: Rented, Free.
- **FR-005**: System MUST allow retrieval of a single bike record by its unique ID.
- **FR-006**: System MUST allow retrieval of all bike records in the fleet as a collection, with optional filtering by State (Rented / Free) and/or Type (Cross / Mountain / Street). When no filter is provided, all bikes are returned.
- **FR-007**: System MUST allow full or partial update of a bike's fields (including state transitions) identified by ID.
- **FR-008**: System MUST allow permanent deletion of a bike record by its unique ID.
- **FR-009**: System MUST return a clear "not found" response when an operation targets a bike ID that does not exist.
- **FR-010**: System MUST return descriptive error responses for all validation failures as plain JSON objects with an `error` key identifying which field(s) failed and why. Success responses MUST return the bike object directly (no envelope wrapper); collection responses MUST return a plain JSON array.
- **FR-011**: System MUST persist all bike records durably so that records survive service restarts.
- **FR-012**: System MUST expose its operations through a well-defined HTTP interface consumable by both frontend clients and internal services in the rental platform.
- **FR-013**: System MUST be packaged as a self-contained, portable deployable unit suitable for orchestration in a container-based infrastructure.

### Key Entities

- **Bike**: Represents a physical bicycle in the rental fleet. Attributes: unique ID (UUID, system-generated), Brand (free text), Type (enumerated: Cross / Mountain / Street), Colour (free text), State (enumerated: Rented / Free).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four CRUD operations respond correctly for valid inputs within 1 second under normal operating load.
- **SC-002**: All invalid inputs (wrong enum values, missing required fields) are rejected with human-readable error messages 100% of the time.
- **SC-003**: Bike records persist across service restarts — no data loss occurs when the service is stopped and restarted.
- **SC-004**: The service handles at least 100 concurrent requests without data corruption or loss of records.
- **SC-005**: A new instance of the service can be deployed in a fresh environment without manual data store configuration steps beyond supplying connection credentials.
- **SC-006**: The service integrates without code changes into the existing rental platform's inter-service communication pattern.

## Assumptions

- The service is consumed by both frontend clients and internal services (e.g., a rental orchestration service); all consumers have full CRUD access.
- Authentication uses JWT tokens validated upstream (API gateway or service mesh); this microservice does not perform its own auth validation — JWT security is out of scope for this spec.
- Data store connection details (host, port, credentials, database name) are supplied via environment variables at deployment time, not hardcoded.
- Bike IDs are UUIDs (v4), system-generated at creation time and are not provided by the caller.
- Only a single data store instance is required for the initial implementation; replication and failover are out of scope for this phase.
- The service is deployed in the same Kubernetes cluster as the other rental microservices and communicates over the cluster's internal network.
- Schema migrations are applied automatically as part of the service startup sequence.
- No soft-delete mechanism is required; deletion is permanent and immediate.
- Concurrent state conflict resolution is out of scope; it is handled by an external async message broker (RabbitMQ) at the platform level.
- CORS is handled at the API gateway / Kubernetes ingress layer; this microservice does not set CORS headers.
- The portable unit packaging requirement means the service and all its runtime dependencies are bundled into a single container image.
