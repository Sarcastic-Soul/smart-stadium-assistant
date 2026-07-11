# Smart Stadium Assistant Architecture

## System Overview

The Smart Stadium Assistant (SSA) is a Generative-AI-driven platform designed for FIFA World Cup 2026 tournament operations. It provides real-time navigation, crowd analytics, sustainability monitoring, multilingual Q&A, and operational alerting.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Cloud (GKE)                       │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   Ingress    │───▶│    Frontend      │    │ Secret Mgr    │  │
│  │  (GCLB+TLS) │    │  (React+Nginx)   │    │  CSI Driver   │  │
│  │              │    │    2 replicas     │    └───────┬───────┘  │
│  │              │    └──────────────────┘            │          │
│  │              │                                    │          │
│  │              │    ┌──────────────────┐    ┌───────▼───────┐  │
│  │    /api/*    │───▶│    Backend       │◀──▶│  API Key      │  │
│  │              │    │  (FastAPI+Uvi)   │    │  (mounted)    │  │
│  │              │    │    3 replicas     │    └───────────────┘  │
│  └──────────────┘    └───────┬──────────┘                       │
│                              │                                  │
│                    ┌─────────▼──────────┐                       │
│                    │  Anthropic Claude  │                       │
│                    │    (External API)  │                       │
│                    └────────────────────┘                       │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐                       │
│  │ CloudSQL     │    │ Artifact Registry│                       │
│  │ (optional)   │    │ (Docker images)  │                       │
│  └──────────────┘    └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Frontend (React + TypeScript)
- **Chat** – Conversational AI interface with SSE streaming, route visualization
- **Map** – SVG-based stadium floor plan with live crowd-density heat-map
- **Dashboard** – Sustainability metrics (energy, water, waste) and operational alerts
- **i18n** – EN, ES, FR, DE translations via `react-i18next`

### Backend (FastAPI + Python 3.11)
- **Chat Router** – Rate-limited (10 req/min), input-sanitised, multilingual
- **Sensors Router** – Crowd density, sustainability metrics, operational alerts
- **LLM Service** – Anthropic Claude integration with connection pooling & fallback
- **Simulators** – Time-varying procedural data for all sensor types
- **Security** – CSI-mounted secrets, XSS filtering, CORS lockdown

### Infrastructure (Terraform + GKE)
- GKE Autopilot cluster with Workload Identity
- Secret Manager with CSI driver integration
- Artifact Registry for Docker images
- Optional CloudSQL PostgreSQL for persistence

## Data Flow

1. User sends a message via the Chat UI
2. Frontend POSTs to `/api/v1/chat/` with message + language
3. Backend sanitises input, rate-checks, and calls the LLM service
4. LLM service detects facility keywords → generates navigation routes
5. If API key present: calls Anthropic Claude; else: uses simulated response
6. Response (with optional route waypoints) returned to frontend
7. Frontend renders the reply and any navigation route polyline

## Security Architecture

- **No hard-coded secrets** – API key loaded from CSI mount or env var
- **Rate limiting** – 10 req/min per IP on chat, 60 req/min default
- **Input sanitisation** – XSS/injection pattern stripping
- **CORS** – Locked to frontend domain
- **CSP** – Strict Content-Security-Policy in nginx
- **Non-root containers** – Backend runs as `appuser`
- **Workload Identity** – GKE SA bound to GCP SA for secret access
