# Deployment Guide (Vercel)

The Smart Stadium Assistant is configured to be deployed as a unified monorepo on **Vercel**. This means the frontend (Vite/React) and the backend (FastAPI/Python) share the exact same Vercel project and domain.

## Why Vercel?
* **Zero CORS Configuration**: Both the React frontend and the FastAPI backend run on the exact same domain. 
* **Serverless Scale**: The FastAPI app is dynamically converted into a Serverless Function (`api/index.py`), which spins up on demand and scales infinitely without paying for idle Kubernetes clusters.
* **Simplified CI/CD**: A single `git push` builds the frontend and provisions the Python backend.

---

## Deployment Steps

### 1. Prerequisites
* A GitHub repository containing the codebase.
* A free Vercel account linked to your GitHub.
* A Groq API Key (for the LLM).

### 2. Vercel Project Setup
1. Log in to Vercel and click **Add New... -> Project**.
2. Select your GitHub repository.
3. In the **Configure Project** screen, use the following settings:
    * **Framework Preset**: `Vite`
    * **Root Directory**: `./` (The root of the repo)
    * **Build Command**: `cd frontend && npm install && npm run build`
    * **Output Directory**: `frontend/dist`
    * **Install Command**: Leave empty (Vercel handles `Pipfile` automatically).

### 3. Environment Variables
Add the following variable in the Vercel Dashboard:
* `GROQ_API_KEY`: Your key from console.groq.com.

### 4. Deploy
Click **Deploy**. Vercel will automatically:
1. Detect the `Pipfile` at the root and spin up a Python 3.12 environment.
2. Install the backend requirements (FastAPI, Pydantic, httpx).
3. Detect `vercel.json` and map `/api/(.*)` to `api/index.py`.
4. Run the Vite build command and serve `frontend/dist` as static files on the root domain.

---

## Local Development vs. Production
* **Local**: You run `npm run dev` and `uvicorn` separately. The frontend connects via a Vite proxy rule (`vite.config.ts`) pointing `/api` to `localhost:8080`.
* **Production**: Vercel's Edge Network handles the routing via the rules specified in `vercel.json`.
