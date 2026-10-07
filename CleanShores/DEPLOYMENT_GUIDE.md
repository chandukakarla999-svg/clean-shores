# 🚀 CleanShores — Deployment Guide: Localhost to Live Website

This guide walks you through deploying **CleanShores** to a live website on the internet for free.

---

## 🎯 Quick Option A: Deploy to Render (Recommended — 100% Free & Fast)

[Render](https://render.com) provides free hosting for Python/Flask web apps and PostgreSQL databases.

### Step 1: Push Code to GitHub
1. In your terminal inside `CleanShores`:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for CleanShores live deployment"
   ```
2. Create a new repository on [GitHub](https://github.com) named `cleanshores`.
3. Push your repository:
   ```bash
   git remote add origin https://github.com/<your-username>/cleanshores.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository `cleanshores`.
4. Configure the service:
   - **Name**: `cleanshores` (or any name you choose)
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: **Free**
5. Add Environment Variables (under **Advanced** -> **Add Environment Variable**):
   - `SECRET_KEY`: `your-random-production-secret-key-2026`
   - `FLASK_DEBUG`: `0`
6. Click **Create Web Service**!
   Render will build the app, install dependencies, auto-create database tables, auto-seed demo accounts, and provide you with a live HTTPS URL (e.g. `https://cleanshores.onrender.com`).

---

## 🎯 Quick Option B: Deploy to Railway

1. Go to [railway.app](https://railway.app) and log in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `cleanshores`.
4. Railway will automatically detect `Procfile` and `requirements.txt` and deploy!
5. In the project settings, click **Generate Domain** to get your public live URL (e.g., `https://cleanshores.up.railway.app`).

---

## 🎯 Quick Option C: Deploy to PythonAnywhere (No Git Required)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Files** tab and upload your `CleanShores` project ZIP (or git clone in the Bash console).
3. Open a Bash console and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Go to the **Web** tab -> **Add a new web app** -> Select **Flask** -> **Python 3.10/3.11**.
5. Set the WSGI configuration file to point to `wsgi.py`:
   ```python
   import sys
   path = '/home/<your-username>/CleanShores'
   if path not in sys.path:
       sys.path.append(path)

   from wsgi import app as application
   ```
6. Click **Reload** and your site will be live at `https://<your-username>.pythonanywhere.com`.

---

## 🔑 Pre-Configured Live Demo Credentials

Your deployment automatically comes with working accounts:

| Role | Username / Email | Password |
|---|---|---|
| **Organizer** | `organizer@cleanshores.org` (or `organizer_demo`) | `Demo@2026!` |
| **Volunteer** | `volunteer@cleanshores.org` (or `volunteer_demo`) | `Demo@2026!` |
| **System Admin** | `admin@cleanshores.org` (or `admin`) | `Admin@2026!` |

---

## ⚡ What was optimized for deployment:
1. **WSGI Server**: Added `wsgi.py` and `Procfile` running `gunicorn` for high concurrency.
2. **Auto-Database Setup**: Database tables and demo data are auto-generated on startup, so the site never crashes with "table not found".
3. **PostgreSQL Compatibility**: URL schema automatically adapts `postgres://` to `postgresql://` if using hosted cloud databases.
4. **Instant Organizer Access**: Organizers can create accounts and immediately host drives with zero verification roadblocks.
