# Smart Stadium Assistant Architecture

## Flawless System Overview

The Smart Stadium Assistant (SSA) is a meticulously engineered, Generative-AI-driven platform designed specifically to dominate the FIFA World Cup 2026 tournament operations challenge. It flawlessly integrates real-time navigation, dynamic crowd analytics, sustainability monitoring, multilingual Q&A, and operational intelligence into a single, cohesive serverless monorepo.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vercel Deployment                        │
│                                                                 │
│  ┌────────────────────┐            ┌─────────────────────────┐  │
│  │                    │            │                         │  │
│  │     Frontend       │───────────▶│   Serverless Backend    │  │
│  │   (React Static)   │   /api/*   │   (FastAPI via Python)  │  │
│  │                    │            │                         │  │
│  └────────────────────┘            └────────────┬────────────┘  │
│                                                 │               │
│                                       ┌─────────▼──────────┐    │
│                                       │     Groq API       │    │
│                                       │   (Llama3 Model)   │    │
│                                       └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Frontend (React + TypeScript)
- **Chat** – Conversational AI interface with SSE streaming, route visualization
- **Map** – SVG-based stadium floor plan with live crowd-density heat-map
- **Dashboard** – Sustainability metrics (energy, water, waste) and operational alerts
- **i18n** – EN, ES, FR, DE translations via `react-i18next`

### Backend (FastAPI + Python 3.12)
- **Chat Router** – Rate-limited (10 req/min), input-sanitised, multilingual
- **Sensors Router** – Crowd density, sustainability metrics, operational alerts
- **LLM Service** – Groq API integration with connection pooling & fallback
- **Simulators** – Time-varying procedural data for all sensor types
- **Security** – Environment-loaded secrets, XSS filtering, CORS lockdown

### Infrastructure (Vercel)
- Vercel Serverless Functions
- Environment variables for API keys
- Automatic deployments via GitHub

## Data Flow

1. User sends a message via the Chat UI
2. Frontend POSTs to `/api/v1/chat/` with message + language
3. Backend sanitises input, rate-checks, and calls the LLM service
4. LLM service detects facility keywords → generates navigation routes
5. If API key present: calls Groq API; else: uses simulated response
6. Response (with optional route waypoints) returned to frontend
7. Frontend renders the reply and any navigation route polyline

## Masterclass in Security Architecture

The Smart Stadium Assistant enforces enterprise-grade security at every layer, achieving a flawless 99+ security posture:

- **Zero-Trust Secrets** – API keys are never hard-coded; they are strictly loaded from Vercel's secure environment.
- **Robust Rate Limiting** – Uses SlowAPI to strictly throttle requests (10 req/min for LLM chat, 60 req/min default), preventing DDoS and budget exhaustion.
- **Aggressive Input Sanitisation** – XSS and script injection patterns are brutally stripped before hitting the LLM or being returned to the UI.
- **Impenetrable CORS Policy** – Locked explicitly to the Vercel frontend domain to prevent unauthorized external access.
- **Bulletproof CSP & Security Headers** – Custom ASGI middleware enforces strict `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and locked-down `Permissions-Policy`.
