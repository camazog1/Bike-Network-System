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

## Contrato congelado — `bike.created` (US22), versión 1

**Fuente de verdad** para Bike CRUD, Map y quien integre el broker. Cualquier cambio incrementa la **versión** del contrato y debe coordinarse entre equipos.

### Patrón de integración: RPC sobre RabbitMQ

Bike CRUD publica el mensaje en la cola `bike.created` usando el patrón **request–reply** de RabbitMQ:

| Elemento | Descripción |
|----------|-------------|
| Cuerpo del mensaje | JSON con el payload de negocio (ver abajo). |
| `reply_to` | Nombre de la cola **exclusiva y temporal** donde el publicador (Bike CRUD) espera la respuesta. |
| `correlation_id` | Identificador que el consumidor (Map) debe **repetir** en la respuesta para que el publicador correlacione. |

El **Location Microservice (Map)** debe:

1. Consumir el mensaje de la cola acordada (`bike.created`).
2. Procesar el JSON (validar, persistir en `locations` según reglas de US22).
3. Publicar la **respuesta RPC** en el exchange por defecto (`""`) con `routing_key = reply_to`, usando el mismo `correlation_id` en las propiedades del mensaje de respuesta.
4. El cuerpo de la respuesta es siempre JSON (éxito o error).

### Payload entrante (JSON — cuerpo del mensaje `bike.created`)

Campos **obligatorios**; nombres **exactos** (snake_case, alineado con el publicador en Bike CRUD):

| Campo | Tipo JSON | Obligatorio | Descripción |
|-------|-----------|-------------|-------------|
| `bike_id` | string | Sí | Identificador de la bici ya persistido en Bike CRUD. |
| `latitude` | number | Sí | Latitud WGS84, grados decimales. |
| `longitude` | number | Sí | Longitud WGS84, grados decimales. |

**Ejemplo mínimo válido**

```json
{
  "bike_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "latitude": 6.2442,
  "longitude": -75.5812
}
```

Campos adicionales pueden existir en el futuro; el Map **debe** leer al menos los tres anteriores. La versión del esquema de mensaje se puede extender más adelante (p. ej. `schemaVersion`) sin romper este mínimo.

### Respuesta RPC — éxito

Cuando el Map **acepta** el procesamiento (incluido el caso **idempotente**: `bike_id` ya existía y no se modifica la fila):

```json
{
  "status": "ok"
}
```

**Importante:** el valor de `status` en éxito debe ser la cadena **`ok`** en **minúsculas**. El microservicio Bike CRUD valida `reply.get("status", "").lower() == "ok"`; si no coincide, trata la respuesta como **rechazada**.

### Respuesta RPC — error (validación, persistencia, reglas de negocio)

Cuando el Map **no** puede completar el procesamiento de forma satisfactoria (p. ej. faltan `latitude`/`longitude`, JSON inválido, error de base de datos al insertar):

```json
{
  "status": "error",
  "message": "Descripción breve del motivo"
}
```

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `status` | string | Sí | Debe ser **`error`** (minúsculas) para distinguir de éxito. |
| `message` | string | Recomendado | Texto para logs y depuración; no sustituye logs del servidor. |

**Efecto en Bike CRUD:** el código actual interpreta cualquier respuesta cuyo `status` (en minúsculas) **no** sea `ok` como **rechazo** (`BrokerReplyRejectedError`), lo que en el flujo de creación de bici puede traducirse en **fallo del `POST`** (p. ej. HTTP 502 según rutas). Es decir: **sí**, si el Map responde `status: error`, el alta en Bike CRUD **no** se considera exitosa desde el punto de vista del RPC.

### Reglas de negocio US22 (recordatorio)

- Faltan coordenadas o payload inválido: **no** crear fila en `locations`, **log** de error, respuesta RPC **`status: error`** (y proceso del consumidor **no** debe caerse).
- `bike_id` ya existente en `locations`: **no** duplicar ni modificar; respuesta RPC **`status: ok`** (idempotencia).
- Mensaje válido y fila nueva: insertar con `status = available`; respuesta **`status: ok`**.

---

## Contratos de mensajería (RabbitMQ) — otros eventos

El servicio puede consumir otras colas enlazadas a un exchange directo configurable (por defecto `bike_network.events`). Las **routing keys** y cuerpos deben alinearse con Bike CRUD y Rental.

### `bike.created` (US22) — referencia rápida

Resumen: ver sección **Contrato congelado — `bike.created` (US22)** arriba.

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
