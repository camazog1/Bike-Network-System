# Data Model: Bike CRUD API

**Branch**: `001-bike-crud-api` | **Date**: 2026-03-24

---

## Entity: Bike

Represents a physical bicycle in the rental fleet.

### Fields

| Field    | Type                          | Constraints                              | Notes                                      |
|----------|-------------------------------|------------------------------------------|--------------------------------------------|
| `id`     | UUID (stored as CHAR(36))     | Primary key, NOT NULL                    | System-generated (UUID v4); callers must not provide |
| `brand`  | String(100)                   | NOT NULL                                 | Free text; e.g. "Trek", "Giant"            |
| `type`   | Enum(Cross, Mountain, Street) | NOT NULL                                 | Restricted to three accepted values        |
| `colour` | String(50)                    | NOT NULL                                 | Free text; e.g. "Red", "Matte Black"       |
| `state`  | Enum(Rented, Free)            | NOT NULL, DEFAULT Free                   | Lifecycle state; transitions via update    |

### State Transitions

```
Free ──────────► Rented
  ▲                │
  └────────────────┘
```

Both transitions are valid and triggered by an update request. No other state values are accepted. Concurrent conflict resolution is handled externally by an async broker (out of scope).

### Validation Rules

- `brand`: required, non-empty string, max 100 characters
- `type`: required, must be exactly one of `Cross`, `Mountain`, `Street` (case-sensitive)
- `colour`: required, non-empty string, max 50 characters
- `state`: required on creation, must be exactly one of `Rented`, `Free` (case-sensitive)
- `id`: never accepted from the caller; always a system-generated UUID v4 string

---

## SQLAlchemy ORM Model (`app/models/bike.py`)

```python
import enum
import uuid
from app import db  # Flask-SQLAlchemy instance

class BikeType(enum.Enum):
    Cross = "Cross"
    Mountain = "Mountain"
    Street = "Street"

class BikeState(enum.Enum):
    Rented = "Rented"
    Free = "Free"

class Bike(db.Model):
    __tablename__ = "bikes"

    id     = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand  = db.Column(db.String(100), nullable=False)
    type   = db.Column(db.Enum(BikeType), nullable=False)
    colour = db.Column(db.String(50), nullable=False)
    state  = db.Column(db.Enum(BikeState), nullable=False, default=BikeState.Free)
```

---

## Pydantic v2 Schemas (`app/schemas/bike.py`)

### BikeCreate — inbound payload for POST

```python
from pydantic import BaseModel, Field
from app.models.bike import BikeType, BikeState

class BikeCreate(BaseModel):
    brand:  str       = Field(..., min_length=1, max_length=100)
    type:   BikeType
    colour: str       = Field(..., min_length=1, max_length=50)
    state:  BikeState = BikeState.Free
```

### BikeUpdate — inbound payload for PUT (all fields optional)

```python
from typing import Optional

class BikeUpdate(BaseModel):
    brand:  Optional[str]       = Field(None, min_length=1, max_length=100)
    type:   Optional[BikeType]  = None
    colour: Optional[str]       = Field(None, min_length=1, max_length=50)
    state:  Optional[BikeState] = None
```

### BikeResponse — outbound for single-resource endpoints

```python
from uuid import UUID

class BikeResponse(BaseModel):
    id:     str  # UUID v4 as string, e.g. "550e8400-e29b-41d4-a716-446655440000"
    brand:  str
    type:   BikeType
    colour: str
    state:  BikeState

    model_config = {"from_attributes": True}  # enables ORM mode
```

### BikeListResponse — outbound for collection endpoint

```python
from typing import List

class BikeListResponse(BaseModel):
    bikes:     List[BikeResponse]
    total:     int
    page:      int
    page_size: int
```

---

## Migration Strategy

- Flask-Migrate (Alembic) auto-generates migration scripts from SQLAlchemy model diffs.
- Initial migration creates the `bikes` table with all columns and the two MySQL ENUM types.
- `flask db upgrade` is run at container startup (via init container or entrypoint script) to apply pending migrations before traffic is served.
- Migration files live in `migrations/versions/` and are committed to version control.
- Rollback via `flask db downgrade` is possible per migration version.
