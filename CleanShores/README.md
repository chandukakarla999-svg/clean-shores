# 🌊 CleanShores — Citizen-Driven Cleanup Coordination Platform

CleanShores is a modern full-stack web application designed for environmental action, beach cleanups, and community waste segregation tracking. It connects volunteers, eco-organizers, and administrators in a single platform.

---

## 🚀 Quick Deployment to Vercel (Recommended)

Deploy CleanShores to **Vercel** with zero server management:

### Option 1: Deploy with Vercel CLI (Fastest)

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm i -g vercel
   ```

2. **Deploy directly from your project directory**:
   ```bash
   vercel
   ```
   - Follow the prompts (press `Enter` for defaults).
   - Set environment variables when prompted or in the Vercel dashboard:
     - `SECRET_KEY`: `your-random-production-secret-key-2026`
     - `FLASK_DEBUG`: `0`

3. **Deploy to production**:
   ```bash
   vercel --prod
   ```
   You will receive your live URL (e.g., `https://cleanshores.vercel.app`).

---

### Option 2: Deploy via GitHub + Vercel Dashboard

1. **Push your repository to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Prepare CleanShores for production deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Import into Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard) and click **Add New...** -> **Project**.
   - Select your GitHub repository.
   - Framework Preset: **Other**.
   - Root Directory: `./` (or `CleanShores`).

3. **Environment Variables**:
   Under **Environment Variables**, add:
   - `SECRET_KEY`: `your-random-production-secret-key-2026`
   - `FLASK_DEBUG`: `0`
   - *(Optional)* `DATABASE_URL`: Your PostgreSQL connection string (from Neon, Supabase, or Vercel Postgres). If not provided, CleanShores automatically uses SQLite stored in `/tmp/cleanShores.db`.

4. **Click Deploy**:
   Vercel will build the serverless functions and launch your website!

---

## 🔑 Demo Login Accounts

All test accounts are pre-seeded and ready to use immediately:

| Portal | Username / Email | Password | Details |
|---|---|---|---|
| **Organizer** | `organizer@cleanshores.org` | `Demo@2026!` | Verified by default, create drives, manage volunteers |
| **Volunteer** | `volunteer@cleanshores.org` | `Demo@2026!` | Browse drives, join cleanups, view certificates |
| **System Admin** | `admin@cleanshores.org` | `Admin@2026!` | Manage users, events, and reports |

---

## 🛠️ Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the development server
python wsgi.py
# Or with npm:
npm run dev
```

Visit `http://localhost:5000` in your web browser.
