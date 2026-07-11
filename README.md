# 🏟️ Smart Stadium Assistant

> **Generative-AI-driven assistant for FIFA World Cup 2026 tournament operations**

A full-stack platform providing real-time navigation, crowd-density analytics, sustainability monitoring, multilingual Q&A, and operational alerting for stadium staff and fans.

**Vertical:** Smart Stadium – Tournament Operations

---

## 🎯 Problem Statement Alignment & Approach
This solution directly addresses the **Smart Stadium & Tournament Operations** challenge for the FIFA World Cup 2026. 

**Approach and Logic:**
The architecture uses a persona-driven Generative AI core (Groq Llama 3) that contextually adapts its intelligence based on the user's role (Fan, Staff, Volunteer, Organizer).
* **Navigation & Crowd Management:** Real-time simulated crowd telemetry is piped into a live heat-map. The LLM provides intelligent wayfinding algorithms and ETA calculations to help users avoid congestion.
* **Multilingual Accessibility:** Full i18n support (English, Spanish, French, German) combined with the LLM's natural translation ensures an inclusive experience for global attendees.
* **Operational Intelligence:** Live dashboard metrics (sustainability and alerts) give venue staff real-time decision support, allowing them to proactively manage tournament operations.

---

## ✨ Features

| Capability | Description |
|---|---|
| 🗺️ **Navigation Routing** | Turn-by-turn waypoints with ETA to restrooms, food courts, exits, VIP lounges, and more |
| 📊 **Crowd-Density Heat-Map** | Live SVG stadium map with zone-level occupancy and AI-generated recommendations |
| 🌱 **Sustainability Metrics** | Real-time energy, solar, water, waste, recycling, and carbon offset monitoring |
| 💬 **Multilingual Q&A** | AI assistant supporting EN, ES, FR, DE with auto-detection |
| 🚨 **Operational Alerts** | Staff-facing alerts (e.g., "Restroom 12 overflow – dispatch cleaning crew") |

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

You can deploy both the frontend and the backend as a single unified project on Vercel:

### Step 1: Install Vercel CLI (optional)
```bash
npm install -g vercel
```

### Step 2: Configure Environment Variables on Vercel
Set the following environment variable in the Vercel Dashboard or CLI:
* `GROQ_API_KEY`: Your Groq API Key (e.g. starting with `gsk_...`)

### Step 3: Deploy
From the root of the repository:
```bash
vercel
# Follow prompt to link project
# Build Command: cd frontend && npm install && npm run build
# Output Directory: frontend/dist
```

---

## 🧪 Testing

### Backend Tests
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

- **No hard-coded secrets** – API key read from `GROQ_API_KEY` environment variable on Vercel
- **Rate limiting** – 10 req/min per IP on `/chat`, 60 req/min default
- **Input sanitisation** – XSS/injection pattern stripping on all user input
- **CORS** – Restricted to frontend origin only
- **CSP & Security Headers** – Provided via custom ASGI middleware

---

## ♿ Accessibility

- Skip-to-content link on every page
- ARIA labels on all interactive elements
- Keyboard focus order with visible focus indicators
- High-contrast dark color palette (WCAG AA compliant)
- i18n support for EN, ES, FR, DE
- Semantic HTML5 with proper heading hierarchy

---

## 📝 Assumptions

1. **Sensor data is simulated** – Crowd density, sustainability metrics, and alerts are procedurally generated for demonstration
2. **Floor plan is static** – Stadium layout uses a simplified SVG representation
3. **LLM fallback** – When no API key is provided, the app uses deterministic simulated responses
4. **Single stadium** – The current implementation models one venue; multi-venue support is a future enhancement
5. **No persistent storage** – All state is ephemeral

---

## 📄 License

MIT
