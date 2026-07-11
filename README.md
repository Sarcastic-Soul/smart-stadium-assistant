# 🏟️ Smart Stadium Assistant

> **Generative-AI-driven assistant for FIFA World Cup 2026 tournament operations**

A full-stack platform providing real-time navigation, crowd-density analytics, sustainability monitoring, multilingual Q&A, and operational alerting for stadium staff and fans.

**Vertical:** Smart Stadium – Tournament Operations

---

## 🎯 Problem Statement Alignment & Approach

This solution directly addresses the **Smart Stadiums & Tournament Operations** challenge for the FIFA World Cup 2026.

### Chosen Vertical
**Smart Stadiums & Tournament Operations** — enhancing stadium operations and the overall tournament experience for fans, organizers, volunteers, and venue staff.

### Approach and Logic

The core architecture uses a **hybrid intelligence model** — combining deterministic rule-based routing with a persona-driven Generative AI core (Groq Llama 3) that contextually adapts its responses based on the user's role and real-time stadium conditions.

**How Generative AI is leveraged:**

1. **Context-Aware Conversations:** The LLM receives a dynamically constructed system prompt that includes the user's role (Fan/Staff/Volunteer/Organizer), preferred language, conversation history, and live sensor data. This means each response is contextually grounded in the current stadium state.

2. **Role-Based Decision Making:** When a staff member asks "What should I do about the crowd?", the AI receives live crowd-density readings and active alerts, allowing it to generate specific operational recommendations (e.g., "Open auxiliary gate N3 to relieve Section 114"). A fan asking the same question gets a simpler "avoid the North Stand" response.

3. **Hybrid Routing Intelligence:** Facility detection uses a deterministic keyword engine (for speed and reliability), while the conversational layer uses GenAI for natural language understanding and multilingual response generation.

4. **Real-Time Sensor Context Injection:** Before every LLM call, the system queries live crowd density and operational alert data, then injects it into the AI prompt as structured context — enabling data-driven decision support without requiring the LLM to access external APIs.

### How the Solution Works

```
User Journey (Fan):
  1. Fan opens the app and selects their language (EN/ES/FR/DE)
  2. Asks "Where is the nearest restroom?"
  3. Backend detects "restroom" keyword → generates navigation waypoints
  4. LLM generates a natural-language response with ETA
  5. Frontend renders the reply + route polyline on the SVG stadium map

User Journey (Staff):
  1. Staff selects "Staff" persona from the role selector
  2. Asks "What's the current situation?"
  3. Backend injects live crowd density + active alerts into the LLM prompt
  4. LLM generates an operational briefing with zone-specific action items
  5. Staff sees the response alongside real-time dashboard metrics
```

### Assumptions

1. **Sensor data is simulated** — Crowd density, sustainability metrics, and alerts are procedurally generated with time-varying sinusoidal patterns for realistic demonstration
2. **Floor plan is static** — Stadium layout uses a simplified SVG representation of a 60,000-seat venue
3. **LLM fallback** — When no API key is provided, the app uses deterministic simulated responses (demo-safe)
4. **Single stadium** — The current implementation models one venue; multi-venue support is a future enhancement
5. **No persistent storage** — All state is ephemeral (session history is in-memory)
6. **Groq Llama 3 chosen** — Selected for its extremely fast inference speed (~500 tokens/sec) making it ideal for real-time stadium assistance where latency matters

---

## ✨ Features

| Capability | Description |
|---|---|
| 🗺️ **Navigation Routing** | Turn-by-turn waypoints with ETA to restrooms, food courts, exits, VIP lounges, and more |
| 📊 **Crowd-Density Heat-Map** | Live SVG stadium map with zone-level occupancy and AI-generated recommendations |
| 🌱 **Sustainability Metrics** | Real-time energy, solar, water, waste, recycling, and carbon offset monitoring |
| 💬 **Multilingual Q&A** | AI assistant supporting EN, ES, FR, DE with auto-detection |
| 🚨 **Operational Alerts** | Staff-facing alerts (e.g., "Restroom 12 overflow – dispatch cleaning crew") |
| 🎭 **Persona-Based Responses** | Fan, Staff, Volunteer, and Organizer roles receive contextually tailored AI responses |
| ♿ **Accessibility** | WCAG AA compliant with ARIA labels, skip links, keyboard navigation, and screen-reader support |

---

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram.

```
Frontend (React/TS)  ──▶  Backend (FastAPI)  ──▶  Groq API (Llama3)
       │                        │
  Vite + Vercel            Vercel Serverless
       │                        │
   i18n (4 langs)          Sensor Simulators
```

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI, Pydantic, SlowAPI, httpx
- **Frontend:** React 18, TypeScript, Vite, i18next
- **AI/LLM:** Groq API (Llama 3 8B) with deterministic fallback
- **Deployment:** Vercel (Unified Frontend/Backend monorepo)
- **CI/CD:** GitHub Actions (Linting & Testing)

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 20+

### Setup & Run

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GROQ_API_KEY in backend/.env
uvicorn app.main:app --reload --port 8080
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## ☁️ Vercel Deployment

See [docs/deployment.md](docs/deployment.md) for the full deployment guide.

1. **Configure:** Set `GROQ_API_KEY` in Vercel Dashboard environment variables
2. **Build Command:** `cd frontend && npm install && npm run build`
3. **Output Directory:** `frontend/dist`
4. **Deploy:** `vercel` or push to GitHub for automatic deployments

---

## 🧪 Testing

### Backend Tests (85%+ coverage)
```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests (Playwright)
```bash
cd frontend
npx playwright install
npm run test:e2e
```

---

## 🔐 Security

- **No hard-coded secrets** – API key read from `GROQ_API_KEY` environment variable
- **Rate limiting** – 10 req/min per IP on `/chat`, 60 req/min default
- **Input sanitisation** – XSS/injection pattern stripping on all user input
- **CORS** – Restricted to frontend origin only
- **Security Headers** – X-Content-Type-Options, X-Frame-Options, CSP, Referrer-Policy via custom ASGI middleware
- **Pydantic validation** – Strict schema enforcement on all API payloads

---

## ♿ Accessibility

- Skip-to-content link on every page
- ARIA labels on all interactive elements
- Keyboard focus order with visible focus indicators
- High-contrast dark color palette (WCAG AA compliant)
- i18n support for EN, ES, FR, DE
- Semantic HTML5 with proper heading hierarchy
- `<noscript>` fallback for non-JS environments

---

## 📄 License

MIT
