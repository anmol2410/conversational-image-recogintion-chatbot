# Deployment Guide: Frontend (Vercel) + Backend (Render)

## Prerequisites

1. Push your project to **GitHub** (or GitLab).
2. Create accounts: [Vercel](https://vercel.com) and [Render](https://render.com).

---

## Part 1: Deploy Backend on Render

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub account and select your repo

### Step 2: Configure Backend

| Setting | Value |
|---------|-------|
| **Name** | `ai-visual-assistant-api` (or any name) |
| **Region** | Oregon (or nearest) |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Step 3: Environment Variables (optional)

Add in **Environment** tab if you use them:

- `OPENAI_API_KEY` – for LLM (optional)
- `OPENAI_API_BASE` – e.g. `http://localhost:11434/v1` for Ollama (optional)

### Step 4: Deploy

1. Click **Create Web Service**
2. Wait for the first deploy
3. Copy the service URL (e.g. `https://ai-visual-assistant-api.onrender.com`)

**Note:** On free tier, the service may sleep after inactivity; first request can take ~30 seconds.

---

## Part 2: Deploy Frontend on Vercel

### Step 1: Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repo

### Step 2: Configure Frontend

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Create React App |
| **Build Command** | `npm run build` |
| **Output Directory** | `build` |

### Step 3: Environment Variable

Add:

| Name | Value |
|------|-------|
| `REACT_APP_API_URL` | `https://your-backend-name.onrender.com` |

Replace with your actual Render backend URL.

### Step 4: Deploy

1. Click **Deploy**
2. Wait for the build
3. Copy the frontend URL (e.g. `https://your-project.vercel.app`)

---

## Verify

1. Open your Vercel frontend URL.
2. Upload an image and ask a question.
3. If you see "Backend not reachable", check:
   - `REACT_APP_API_URL` is correct and uses `https`
   - Render service is running
   - First load on Render free tier may take a minute (cold start)

---

## Optional: CORS

The backend uses `allow_origins=["*"]`, so any frontend URL works. For stricter security, add your Vercel URL in `backend/main.py`:

```python
allow_origins=[
    "https://your-project.vercel.app",
    "http://localhost:3000"
],
```

---

## Summary

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | `https://your-project.vercel.app` |
| Backend | Render | `https://your-api.onrender.com` |
