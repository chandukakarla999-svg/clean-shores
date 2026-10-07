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

## 🌐 Other Free Deployment Options

- **Render**: Connect repository -> Web Service -> Build Command: `pip install -r requirements.txt` -> Start Command: `gunicorn wsgi:app` -> Done. (See `CleanShores/DEPLOYMENT_GUIDE.md`)
- **Railway**: Connect repository -> One-click deploy detected from `Procfile`.
- **PythonAnywhere**: Upload files -> Configure WSGI pointing to `wsgi:app`.

---

## 🔑 Demo Login Accounts

All test accounts are pre-seeded and ready to use immediately:

| Portal | Username / Email | Password | Details |
|---|---|---|---|
| **Organizer** | `organizer@cleanshores.org` | `Demo@2026!` | Verified by default, create drives, manage volunteers |
| **Volunteer** | `volunteer@cleanshores.org` | `Demo@2026!` | Browse drives, join cleanups, view certificates |
| **System Admin** | `admin@cleanshores.org` | `Admin@2026!` | Manage users, events, and reports |

---

## 🗄️ Database Configuration (MySQL)

CleanShores uses **MySQL** as its primary persistent database engine via PyMySQL and SQLAlchemy.

### Setting Up MySQL:
1. Ensure your MySQL server is running (e.g., via **XAMPP**, **MySQL Server**, **MariaDB**, or cloud provider).
2. Configure credentials in `.env` (or `CleanShores/.env`):
   ```ini
   # Option 1: Full Connection URL
   DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/cleanshores_db

   # Option 2: Individual variables
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=
   MYSQL_DATABASE=cleanshores_db
   ```
3. *Note*: The database `cleanshores_db` will be **automatically created** on MySQL if it does not already exist!

### Migrating Existing Data from SQLite to MySQL:
If you have existing sample data or users in the old SQLite file (`database/cleanShores.db`), you can migrate everything directly into MySQL with a single command:
```bash
npm run migrate:mysql
# Or:
python CleanShores/migrate_sqlite_to_mysql.py
```

---

## 🛠️ Local Development

To run the application locally on your computer:

```bash
# 1. Install dependencies (including pymysql and cryptography)
pip install -r requirements.txt

# 2. Start the development server
npm run dev
# Or directly:
python CleanShores/app.py
```

Visit `http://localhost:5000` in your web browser.

---

## 📁 Project Structure

```
BUGGY RACE/
├── CleanShores/
│   ├── app.py                 # Flask Application Factory
│   ├── config.py              # Production & Environment Config
│   ├── wsgi.py                # Production WSGI Server Entry Point
│   ├── Procfile               # Cloud deployment runner (Render/Railway)
│   ├── vercel.json            # Vercel Serverless Function Config
│   ├── api/index.py           # Vercel Entry Point
│   ├── models/                # SQLAlchemy Models (User, Drive, etc.)
│   ├── routes/                # Blueprint Controllers (auth, organizer, etc.)
│   ├── services/              # Email, verification, notification services
│   ├── static/                # CSS, JS, and UI Assets
│   └── templates/             # Jinja2 HTML Templates
├── api/index.py               # Root Vercel Entry Point
├── vercel.json                # Root Vercel Config
├── requirements.txt           # Python Dependencies
├── package.json               # NPM Script Runner
└── README.md                  # Deployment & Documentation
```

---

## ✨ Features Included

- **No Verification Obstacle for Organizers**: Organizers can sign up and immediately start organizing cleanup drives without admin document approval.
- **Full Mobile Responsiveness**: Complete mobile drawer navigation and touch-friendly interface across smartphones, tablets, and desktops.
- **Dynamic URL Resolution**: All email links and navigation paths automatically adapt to the live domain with zero hardcoded localhost URLs.
- **Production-Ready Serverless**: Compatible with Vercel serverless `/tmp` filesystem and cloud PostgreSQL databases.
