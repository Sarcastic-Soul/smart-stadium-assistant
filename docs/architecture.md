# Smart Stadium Assistant Architecture

## System Overview

The Smart Stadium Assistant (SSA) is a Generative-AI-driven platform designed for FIFA World Cup 2026 tournament operations. It provides real-time navigation, crowd analytics, sustainability monitoring, multilingual Q&A, and Q&A helpers.

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

## Security Architecture

- **No hard-coded secrets** – API key loaded from env var
- **Rate limiting** – 10 req/min per IP on chat, 60 req/min default
- **Input sanitisation** – XSS/injection pattern stripping
- **CORS** – Locked to frontend domain
- **CSP & Security Headers** – Provided via custom ASGI middleware
