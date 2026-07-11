# Smart Stadium Assistant API Documentation

The backend is built with FastAPI and runs as a serverless function on Vercel.

## Base URL
`/api/v1`

---

## 1. Chat Endpoints

### `POST /chat/`
Main conversational endpoint for the Smart Stadium Assistant.

**Request Body (`ChatRequest`)**:
```json
{
  "message": "Where is the nearest restroom?",
  "language": "en", 
  "role": "fan",
  "session_id": "optional-uuid"
}
```
*   `language`: `en`, `es`, `fr`, `de` (default: `en`)
*   `role`: `fan`, `staff`, `volunteer`, `organizer` (default: `fan`)

**Response (`ChatResponse`)**:
```json
{
  "reply": "The nearest restroom is located at Gate C. I've highlighted the route on your map.",
  "language": "en",
  "route": {
    "waypoints": [{"x": 10, "y": 20}, {"x": 30, "y": 40}],
    "eta_minutes": 2.5,
    "distance_meters": 120.0
  }
}
```

### `GET /chat/roles`
Returns a list of supported personas/roles that the LLM can adopt.

**Response**:
```json
[
  {
    "code": "fan",
    "name": "General Fan",
    "description": "Standard match attendee"
  },
  ...
]
```

---

## 2. Sensor Endpoints

These endpoints provide real-time (simulated) telemetry from the stadium.

### `GET /sensors/crowd`
Returns crowd density metrics across different stadium zones.

**Response**:
```json
[
  {
    "zone": "North Gate",
    "density_percent": 85,
    "trend": "increasing",
    "status": "crowded"
  }
]
```

### `GET /sensors/sustainability`
Returns live sustainability metrics (e.g. solar output, water recycled).

**Response**:
```json
[
  {
    "metric": "Solar Output",
    "value": 450,
    "unit": "kW",
    "status": "good"
  }
]
```

### `GET /sensors/alerts`
Returns active operational alerts (e.g., restroom maintenance, security).

**Response**:
```json
[
  {
    "id": "1",
    "severity": "high",
    "message": "Restroom 4 requires immediate cleaning",
    "timestamp": "2026-07-11T12:00:00Z"
  }
]
```

---

## Security

* **Rate Limiting**: The `/chat/` endpoint is rate-limited to 10 requests per minute per IP to prevent LLM abuse.
* **CORS**: The API uses strict CORS rules allowing requests only from configured frontend domains.
* **XSS Protection**: All incoming `message` fields are stripped of HTML/JS injection patterns before reaching the LLM or session memory.
