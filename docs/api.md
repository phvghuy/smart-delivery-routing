# Smart Delivery Routing — API Reference

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

All protected endpoints require the header:
```
Authorization: Bearer <access_token>
```

---

## Authentication

### POST `/auth/login`

Sign in and receive an access token.

**Request**
```json
{
  "email": "admin@example.com",
  "password": "secret"
}
```

**Response `200`**
```json
{
  "access_token": "eyJhbGci...",
  "role": "admin"
}
```

**Error `401`** — wrong email or password
```json
{ "detail": "Invalid credentials." }
```

---

### POST `/auth/logout`

Invalidate the current token. Requires auth.

**Response `204`** — no body

---

## Data Import

### POST `/import/upload`

Upload CSV files to seed the database. Requires admin.

**Request** — `multipart/form-data` with 3 files:

| Field | Content |
|---|---|
| `orders_file` | CSV of orders |
| `vehicles_file` | CSV of vehicles |
| `warehouses_file` | CSV of warehouses |

**CSV columns — orders**

| Column | Type | Description |
|---|---|---|
| `order_id` | string | Unique ID |
| `lat` | float | Delivery latitude |
| `lng` | float | Delivery longitude |
| `weight` | float | Weight in kg |
| `volume` | float | Volume in m³ |

**CSV columns — vehicles**

| Column | Type | Description |
|---|---|---|
| `vehicle_id` | string | Unique ID |
| `max_weight` | float | Capacity in kg |
| `max_volume` | float | Capacity in m³ |
| `start_lat` | float | Warehouse latitude |
| `start_lng` | float | Warehouse longitude |

**CSV columns — warehouses**

| Column | Type | Description |
|---|---|---|
| `warehouse_id` | string | Unique ID |
| `lat` | float | Latitude |
| `lng` | float | Longitude |

**Response `201`**
```json
{
  "imported_orders": 600,
  "imported_vehicles": 30,
  "imported_warehouses": 5
}
```

**Error `400`** — missing or invalid column in a CSV file

---

## Route Optimization

### POST `/optimize`

Run route optimization synchronously. Returns when computation is complete. Requires admin.

> Use this for small datasets (< 100 orders). For larger datasets use `/optimize/async`.

**Response `200`**
```json
{
  "results": [
    {
      "solver": "nearest_neighbor",
      "routes": [
        {
          "vehicle_id": "VEH-001",
          "stops": [
            { "order_id": "ORD-042", "lat": 10.78, "lng": 106.70 },
            { "order_id": "ORD-017", "lat": 10.81, "lng": 106.73 }
          ],
          "total_distance_km": 12.4
        }
      ],
      "unassigned_orders": ["ORD-099"],
      "kpi": {
        "total_distance_km": 284.5,
        "vehicles_used": 8,
        "unassigned_count": 1,
        "average_fill_rate_weight": 0.74,
        "average_fill_rate_volume": 0.68,
        "per_vehicle": [
          {
            "vehicle_id": "VEH-001",
            "stops_count": 12,
            "distance_km": 34.2,
            "fill_rate_weight": 0.82,
            "fill_rate_volume": 0.71
          }
        ]
      }
    }
  ]
}
```

---

### POST `/optimize/async`

Submit an optimization job to the background worker. Returns immediately with a `job_id`. Requires admin.

**Response `202`**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

Poll `/jobs/{job_id}` to check progress.

---

### GET `/jobs/{job_id}`

Check the status of an async optimization job. Requires admin.

**Response `200`**

| `status` | Meaning |
|---|---|
| `pending` | Job is queued or running |
| `success` | Job finished successfully |
| `failure` | Job threw an error |
| `expired` | Result was evicted from cache (TTL: 24h) |

**While pending:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "result": null,
  "error": null
}
```

**On success** — `result` has the same structure as `POST /optimize`:
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "success",
  "result": { "results": [ ... ] },
  "error": null
}
```

**On failure:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "failure",
  "result": null,
  "error": "NoPendingOrders: no orders with status PENDING found"
}
```

**Error `404`** — job ID not found
```json
{ "detail": "Job not found." }
```

---

## Typical Admin Dashboard Flow

```
1. POST /auth/login              → lưu access_token
2. POST /import/upload           → upload CSV, nhận imported counts
3. POST /optimize/async          → nhận job_id
4. Poll GET /jobs/{job_id}       → đợi status = "success"
5. Render routes và KPI từ result
```

**Polling recommendation:** gọi mỗi 2–5 giây, dừng khi `status !== "pending"`.
