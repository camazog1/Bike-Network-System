# API Contract: Bike CRUD API

**Branch**: `001-bike-crud-api` | **Date**: 2026-03-24
**Base URL**: `/api/v1`
**Content-Type**: `application/json` (all requests and responses)

---

## Common Conventions

### Error Envelope (all non-2xx responses)

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable description of what went wrong.",
  "details": {}
}
```

Common error codes:

| HTTP Status | Code                | When                                         |
|-------------|---------------------|----------------------------------------------|
| 400         | `BAD_REQUEST`       | Malformed JSON body or non-JSON request       |
| 404         | `BIKE_NOT_FOUND`    | No bike exists with the given ID              |
| 422         | `VALIDATION_ERROR`  | Pydantic validation failure (invalid fields)  |
| 500         | `INTERNAL_ERROR`    | Unhandled server error                        |

### Pagination (collection endpoints)

Query parameters:

| Parameter   | Type    | Default | Description                      |
|-------------|---------|---------|----------------------------------|
| `page`      | integer | `1`     | 1-based page number              |
| `page_size` | integer | `20`    | Number of items per page (max 100) |

Response always includes `total`, `page`, and `page_size` alongside the items array.

---

## Endpoints

---

### POST /api/v1/bikes

Create a new bike in the fleet.

**Request Body**

```json
{
  "brand":  "Trek",
  "type":   "Mountain",
  "colour": "Red",
  "state":  "Free"
}
```

| Field    | Type   | Required | Accepted Values                    |
|----------|--------|----------|------------------------------------|
| `brand`  | string | Yes      | Non-empty, max 100 chars           |
| `type`   | string | Yes      | `Cross`, `Mountain`, `Street`      |
| `colour` | string | Yes      | Non-empty, max 50 chars            |
| `state`  | string | No       | `Rented`, `Free` (default: `Free`) |

**Responses**

`201 Created`
```json
{
  "id":     "550e8400-e29b-41d4-a716-446655440000",
  "brand":  "Trek",
  "type":   "Mountain",
  "colour": "Red",
  "state":  "Free"
}
```

`422 Unprocessable Entity`
```json
{
  "code":    "VALIDATION_ERROR",
  "message": "Invalid value for field 'type'.",
  "details": { "field": "type", "value": "BMX", "accepted": ["Cross", "Mountain", "Street"] }
}
```

---

### GET /api/v1/bikes

Retrieve all bikes, with optional filters and pagination.

**Query Parameters**

| Parameter   | Type    | Required | Accepted Values               | Description                     |
|-------------|---------|----------|-------------------------------|---------------------------------|
| `state`     | string  | No       | `Rented`, `Free`              | Filter by bike state            |
| `type`      | string  | No       | `Cross`, `Mountain`, `Street` | Filter by bike type             |
| `page`      | integer | No       | ≥ 1 (default: `1`)            | Page number                     |
| `page_size` | integer | No       | 1–100 (default: `20`)         | Items per page                  |

**Response**

`200 OK`
```json
{
  "bikes": [
    {
      "id":     "550e8400-e29b-41d4-a716-446655440000",
      "brand":  "Trek",
      "type":   "Mountain",
      "colour": "Red",
      "state":  "Free"
    }
  ],
  "total":     42,
  "page":      1,
  "page_size": 20
}
```

When no bikes match the filters, `bikes` is an empty array and `total` is `0`.

`422 Unprocessable Entity` — returned if a filter value is outside the accepted enum values.

---

### GET /api/v1/bikes/{id}

Retrieve a single bike by ID.

**Path Parameters**

| Parameter | Type   | Description            |
|-----------|--------|------------------------|
| `id`      | string | Bike's UUID (v4)       |

**Responses**

`200 OK`
```json
{
  "id":     "550e8400-e29b-41d4-a716-446655440000",
  "brand":  "Trek",
  "type":   "Mountain",
  "colour": "Red",
  "state":  "Free"
}
```

`404 Not Found`
```json
{
  "code":    "BIKE_NOT_FOUND",
  "message": "No bike found with id 550e8400-e29b-41d4-a716-446655440000.",
  "details": { "id": "550e8400-e29b-41d4-a716-446655440000" }
}
```

---

### PUT /api/v1/bikes/{id}

Update one or more fields of an existing bike. All fields are optional; omitted fields are left unchanged.

**Path Parameters**

| Parameter | Type   | Description       |
|-----------|--------|-------------------|
| `id`      | string | Bike's UUID (v4)  |

**Request Body** (all fields optional)

```json
{
  "state": "Rented"
}
```

| Field    | Type   | Required | Accepted Values               |
|----------|--------|----------|-------------------------------|
| `brand`  | string | No       | Non-empty, max 100 chars      |
| `type`   | string | No       | `Cross`, `Mountain`, `Street` |
| `colour` | string | No       | Non-empty, max 50 chars       |
| `state`  | string | No       | `Rented`, `Free`              |

**Responses**

`200 OK` — returns the full updated bike object
```json
{
  "id":     "550e8400-e29b-41d4-a716-446655440000",
  "brand":  "Trek",
  "type":   "Mountain",
  "colour": "Red",
  "state":  "Rented"
}
```

`404 Not Found` — bike ID does not exist
`422 Unprocessable Entity` — a provided field value fails validation

---

### DELETE /api/v1/bikes/{id}

Permanently remove a bike from the fleet.

**Path Parameters**

| Parameter | Type   | Description       |
|-----------|--------|-------------------|
| `id`      | string | Bike's UUID (v4)  |

**Responses**

`204 No Content` — bike successfully deleted; empty body.

`404 Not Found`
```json
{
  "code":    "BIKE_NOT_FOUND",
  "message": "No bike found with id 550e8400-e29b-41d4-a716-446655440000.",
  "details": { "id": "550e8400-e29b-41d4-a716-446655440000" }
}
```

---

### GET /api/v1/health

Lightweight liveness/readiness probe for Kubernetes.

**Response**

`200 OK`
```json
{ "status": "ok" }
```

No authentication required. Used by Kubernetes `readinessProbe` and `livenessProbe`.
