# API — Map / Location Microservice

Microservicio de geolocalización del **Bike Network System**. Expone REST JSON bajo **`/api/v1`** para el mapa (Leaflet) y consume eventos asíncronos vía **RabbitMQ**.

**Base URL (desarrollo local típico):** `http://localhost:8081`  
**Prefijo de versión:** `/api/v1`

---

## Autenticación (HTTP)

Las historias de usuario del mapa describen un endpoint de **solo lectura** de ubicaciones disponibles. La decisión de **exigir JWT** en ese `GET` o dejarlo público debe alinearse con el documento de NFR del proyecto (p. ej. RNF-04). Si el endpoint queda protegido, el cliente debe enviar:

`Authorization: Bearer <JWT>`

---

## Convenciones de respuesta de error

Salvo cuando no aplica (p. ej. `204`), los errores siguen el formato común del proyecto:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | string | Código de error (p. ej. `VALIDATION_ERROR`, `NOT_FOUND`). |
| `message` | string | Mensaje legible. |
| `details` | object | Información adicional (p. ej. lista de errores de validación). |

---

## Endpoints REST

### `GET /api/v1/health`

Comprobación de vida del servicio (orquestación, balance, probes).

**Respuesta (200 OK)**

```json
{
  "status": "ok"
}
```

| Código | Descripción |
|--------|-------------|
| 200 | Servicio operativo. |

---

### `GET /api/v1/locations/available`

Devuelve las bicicletas **con `status = available`** y sus coordenadas, en formato apto para consumo directo por el frontend (p. ej. marcadores Leaflet).

**Respuesta (200 OK)**

Cuerpo: **array JSON** (no un objeto envolvente). Cada elemento:

| Campo (JSON) | Tipo | Descripción |
|--------------|------|-------------|
| `bikeId` | string | Identificador de la misma bici que en el dominio Bike CRUD (hasta 36 caracteres en persistencia). |
| `latitude` | number | Latitud en grados decimales (WGS84). |
| `longitude` | number | Longitud en grados decimales (WGS84). |

**Ejemplo**

```json
[
  {
    "bikeId": "BIKE-MOCK-001",
    "latitude": 6.2442,
    "longitude": -75.5812
  }
]
```

**Casos límite**

| Situación | Código HTTP | Cuerpo |
|-----------|-------------|--------|
| No hay filas en la tabla `locations` | 200 | `[]` |
| Hay bicis pero ninguna `available` | 200 | `[]` |
| Hay bicis `available` | 200 | Array con uno o más objetos `{ bikeId, latitude, longitude }` |

---

## Modelo de datos persistido (referencia)

Tabla **`locations`** (MySQL, esquema `geo_db` en despliegue objetivo):

| Columna | Tipo lógico | Notas |
|---------|---------------|--------|
| `bike_id` | string (PK) | Misma identidad que la bici en Bike CRUD. |
| `latitude` | float | Obligatorio. |
| `longitude` | float | Obligatorio. |
| `status` | enum | `available` \| `unavailable` (por defecto `available` al crear vía evento). |

---

## Contratos de mensajería (RabbitMQ)

El servicio está pensado para **consumir** colas enlazadas a un exchange directo configurable (por defecto `bike_network.events`). Las **routing keys** y el cuerpo deben acordarse con Bike CRUD y Rental; los valores objetivo alineados con las HU y el diagrama de despliegue son:

### `bike.created` (US22)

Publicado por Bike CRUD al registrar una bici. El map debe **crear** un registro en `locations` si no existe.

**Payload esperado (mínimo)**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `bikeId` | string | Sí | Identificador de la bici. |
| `latitude` | number | Sí | Latitud válida. |
| `longitude` | number | Sí | Longitud válida. |

**Comportamiento esperado**

- Si faltan coordenadas o el mensaje es inválido: **log de error**, **no** crear fila, **no** detener el proceso del consumidor.
- Si ya existe `bikeId`: **no** duplicar ni modificar (idempotencia silenciosa).
- Si el mensaje es válido: insertar fila con `status = available`.

*(Nota: el formato exacto del JSON puede incluir metadatos adicionales; el consumidor debe extraer `bikeId`, `latitude`, `longitude` de forma consistente con Bike CRUD.)*

---

### `bike.statusUpdated` (US23)

Publicado por Bike CRUD al cambiar disponibilidad de la bici en el dominio de mapa.

**Payload esperado (mínimo)**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `bikeId` | string | Sí | Identificador de la bici. |
| `status` | string | Sí | Solo `available` o `unavailable`. |

**Comportamiento esperado**

- Actualizar solo el campo `status` del registro existente.
- Si no existe fila para `bikeId`: **log de warning**, sin cambios en BD.
- Si `status` no es `available` ni `unavailable`: **log de error**, sin modificar la fila.

---

### Eventos adicionales (diagrama de despliegue)

| Routing key | Rol |
|-------------|-----|
| `bike.deleted` | Eliminar o marcar la ubicación asociada al `bikeId` (según decisión de equipo). |
| `rental.completed` | Actualizar posición o estado según reglas de negocio acordadas. |

Las variables de entorno `RABBITMQ_ROUTING_KEY_*` permiten ajustar nombres sin cambiar código.

---

## Variables de entorno relevantes

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URI SQLAlchemy (p. ej. MySQL `geo_db`). |
| `PORT` | Puerto HTTP del servicio (por defecto `8081`). |
| `RABBITMQ_URL` | URL AMQP del broker. |
| `RABBITMQ_EXCHANGE` | Exchange directo para bindings. |
| `RABBITMQ_ROUTING_KEY_*` | Routing keys de cada cola consumida. |
| `ENABLE_RABBIT_CONSUMERS` | `1` / `true` / `yes` para arrancar consumidores en segundo plano. |

---

## Referencias

- HU **US22**, **US23**, **US24** (product backlog).
- Decisiones de arquitectura: `docs/Architectural Decision Technology Stack & Development Practices.md`.
- Código del microservicio: `micro-services/map/`.
