# Complete Beginner's Guide: Deploy Frontend + Backend

This guide assumes you have **no experience** with deployment. Follow the steps in order.

---

## What You Need First

1. **Your code on GitHub**  
   Your project should already be on GitHub at:  
   `https://github.com/anmol2410/conversational-image-recogintion-chatbot`

2. **Two free accounts** (use your email or Google):
   - **Render** (for backend): https://render.com → Sign Up
   - **Vercel** (for frontend): https://vercel.com → Sign Up

---

# PART 1: Deploy the BACKEND (Render)

The backend is the Python/FastAPI server that runs your AI (YOLO, etc.). Render will run it on the internet.

---

## Step 1: Open Render

1. Go to **https://dashboard.render.com**
2. Log in (or sign up with GitHub — it’s easiest).

---

## Step 2: Create a New Web Service

1. Click the blue **New +** button (top right).
2. Click **Web Service**.

---

## Step 3: Connect Your GitHub Repo

1. Under **Connect a repository**, you’ll see “GitHub”.
2. If it says “Configure account”, click it and allow Render to see your repos.
3. Find **conversational-image-recogintion-chatbot** in the list.
4. Click **Connect** next to it.

---

## Step 4: Fill In the Settings

Use these **exact** values:

| What you see on screen | What to enter |
|------------------------|---------------|
| **Name** | `ai-visual-assistant-api` (or any name you like) |
| **Region** | Leave default (e.g. Oregon) |
| **Branch** | `master` |
| **Root Directory** | Click “Add” or type: `backend` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Important:**  
- **Root Directory** must be `backend` (the folder where your Python code is).  
- **Start Command** must be exactly as above (copy-paste it).

---

## Step 5: Create the Service

1. Scroll down.
2. Click **Create Web Service**.
3. Wait 5–10 minutes. Render is installing Python packages and your app. The first time is slow.
4. When the top of the page shows **Live** in green, the backend is deployed.

---

## Step 6: Copy Your Backend URL

1. At the top of the page you’ll see a URL, for example:  
   `https://ai-visual-assistant-api.onrender.com`
2. **Copy this URL** and save it in Notepad.  
   You will need it for the frontend (Part 2).

**Note:** On the free plan, the backend “sleeps” if no one uses it. The first request after sleep can take 30–60 seconds.

---

# PART 2: Deploy the FRONTEND (Vercel)

The frontend is the React website users see. Vercel will build it and give you a link.

---

## Step 1: Open Vercel

1. Go to **https://vercel.com**
2. Log in (or sign up with GitHub — easiest).

---

## Step 2: Add a New Project

1. Click **Add New…** (top right).
2. Click **Project**.

---

## Step 3: Import Your GitHub Repo

1. You’ll see a list of your GitHub repositories.
2. Find **conversational-image-recogintion-chatbot**.
3. Click **Import** next to it.

---

## Step 4: Configure the Project

**Before** clicking Deploy, set these:

### 4.1 Root Directory

- Find **Root Directory**.
- Click **Edit**.
- Type: `frontend`
- Confirm.  
  This tells Vercel: “My React app is inside the `frontend` folder.”

### 4.2 Build and Output (usually correct by default)

- **Build Command:** leave as is, or set to `npm run build`
- **Output Directory:** leave as is, or set to `build`  
  (Do **not** use `cd frontend` in the commands — Root Directory is already `frontend`.)

### 4.3 Environment Variable (important)

1. Open **Environment Variables**.
2. **Name:** `REACT_APP_API_URL`  
3. **Value:** paste the **backend URL** you copied from Render (e.g. `https://ai-visual-assistant-api.onrender.com`)  
   - No slash at the end.  
   - Must start with `https://`.
4. Save / Add.

---

## Step 5: Deploy

1. Click **Deploy**.
2. Wait a few minutes. Vercel is building your React app.
3. When you see **Congratulations!**, the frontend is deployed.

---

## Step 6: Copy Your Frontend URL

1. You’ll see a link like:  
   `https://conversational-image-recogintion-chatbot.vercel.app`
2. Click **Visit** or copy that URL.  
   That’s your live app.

---

# PART 3: Test Your Live App

1. Open the **Vercel URL** (frontend) in your browser.
2. Upload an image and ask a question.
3. If it works: you’re done.
4. If you see **“Backend not reachable”**:
   - Wait 30–60 seconds and try again (Render might be waking up).
   - In Vercel → your project → **Settings** → **Environment Variables**, check that `REACT_APP_API_URL` is exactly your Render URL with `https://`.
   - Redeploy the frontend after changing the variable.

---

# Quick Reference

| What | Where | URL you get |
|------|--------|-------------|
| Backend | Render | `https://something.onrender.com` |
| Frontend | Vercel | `https://something.vercel.app` |

**Order:**  
1. Deploy backend (Render) first.  
2. Copy backend URL.  
3. Deploy frontend (Vercel) and set `REACT_APP_API_URL` to that URL.

If you get stuck, say which step you’re on and what you see on the screen.
