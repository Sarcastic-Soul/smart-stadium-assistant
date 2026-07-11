# 🏟️ Smart Stadium Assistant

> **Generative-AI-driven assistant for FIFA World Cup 2026 tournament operations**

A full-stack platform providing real-time navigation, crowd-density analytics, sustainability monitoring, multilingual Q&A, and operational alerting for stadium staff and fans.

**Vertical:** Smart Stadium – Tournament Operations

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
Frontend (React/TS)  ──▶  Backend (FastAPI)  ──▶  Anthropic Claude
       │                        │
   Vite + Nginx            Uvicorn (async)
       │                        │
   i18n (4 langs)          Sensor Simulators
```

**Tech Stack:**
- **Backend:** Python 3.11, FastAPI, Pydantic, SlowAPI, httpx
- **Frontend:** React 18, TypeScript, Vite, i18next
- **Infrastructure:** Terraform, GKE Autopilot, Secret Manager, Artifact Registry
- **CI/CD:** GitHub Actions → Docker → GKE

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+, Node 20+, Docker (optional)

### Option 1: Docker Compose
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your CLONEMODEL_API_KEY (optional for demo mode)

docker compose up
# Frontend: http://localhost:3000
# Backend:  http://localhost:8080/docs
```

### Option 2: Run Separately

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
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

## ☁️ GCP Deployment

### Target Project
- **Project ID:** `promptwars-493516`
- **Project Number:** `139415254857`
- **Region:** `us-central1`

### Step 1: Create Terraform State Bucket
```bash
gsutil mb -p promptwars-493516 -l us-central1 gs://promptwars-tf-state
```

### Step 2: Populate Secret Manager
```bash
gcloud secrets create CLONEMODEL_API_KEY \
  --project=promptwars-493516 \
  --replication-policy=automatic

echo -n "YOUR_ANTHROPIC_API_KEY" | \
  gcloud secrets versions add CLONEMODEL_API_KEY \
  --project=promptwars-493516 \
  --data-file=-
```

### Step 3: Deploy Infrastructure
```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

### Step 4: Build & Push Images
```bash
REGISTRY=us-central1-docker.pkg.dev/promptwars-493516/smart-stadium

gcloud auth configure-docker us-central1-docker.pkg.dev

docker build -t $REGISTRY/backend:latest backend/
docker push $REGISTRY/backend:latest

docker build -t $REGISTRY/frontend:latest frontend/
docker push $REGISTRY/frontend:latest
```

### Step 5: Deploy to GKE
```bash
gcloud container clusters get-credentials smart-stadium-gke \
  --region us-central1 --project promptwars-493516

kubectl apply -f infra/k8s/deployment.yaml
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

- **No hard-coded secrets** – API key read from GCP Secret Manager CSI mount (`/secrets/CLONEMODEL_API_KEY`) or environment variable
- **Rate limiting** – 10 req/min per IP on `/chat`, 60 req/min default
- **Input sanitisation** – XSS/injection pattern stripping on all user input
- **CORS** – Restricted to frontend origin only
- **CSP** – Strict Content-Security-Policy headers via nginx
- **Non-root containers** – Backend runs as unprivileged `appuser`
- **Workload Identity** – GKE service account bound to GCP IAM for secret access

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
5. **No persistent storage** – CloudSQL is optional and disabled by default; all state is ephemeral

---

## 📄 License

MIT
