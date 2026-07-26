# BHEL Project Monitoring System

A production-grade project monitoring platform for BHEL (Bharat Heavy Electricals Limited) EPC / power-plant execution, built with Flask and modeled on the workflows of enterprise industrial systems such as **Primavera P6**, **SAP PM**, and **Siemens Teamcenter**.

The system tracks a project's complete execution hierarchy:

```
Project → Unit → Area → System → Equipment
```

At the leaf (Equipment) level, engineers log installation & commissioning progress daily, weekly and monthly, upload site photographs, QA documents and engineering drawings, and management reviews everything through a real-time dashboard with KPI cards, charts, a progress timeline, and printable PDF / Excel reports.

---

## Feature Summary

| Area | Capabilities |
|---|---|
| **Authentication & RBAC** | Flask-Login sessions, Bcrypt password hashing, three roles: **Admin**, **Engineer**, **Viewer** |
| **Hierarchy Master Data** | Projects, Units, Areas, Systems, Equipment Categories, Equipment Master, Vendor Master |
| **Progress Tracking** | Daily / Weekly / Monthly progress logs with automatic roll-up of progress percentages up the hierarchy |
| **Attachments** | Photo, Document and Drawing upload per equipment record |
| **Data Exchange** | Styled Excel export/import (openpyxl) of the Equipment Master, downloadable import template |
| **Reporting** | Per-project PDF progress report (ReportLab) with hierarchy + equipment status tables |
| **Dashboard** | KPI cards, equipment status pie chart, project progress bar chart, progress gauges, upcoming deadlines, recent activity timeline, project card grid |
| **Notifications** | In-app notification bell with auto-generated deadline / overdue alerts |
| **Audit Trail** | Every create/update/delete/login action logged with user, IP address and timestamp |
| **Search / Filter / Pagination** | Present across all master-data list views |

---

## Technology Stack

**Backend:** Flask · SQLAlchemy · Flask-Login · Flask-Bcrypt · Flask-Migrate · Flask-WTF
**Database:** PostgreSQL (production) / SQLite (development)
**Frontend:** Bootstrap 5 · vanilla JavaScript · Chart.js · DataTables
**Documents:** openpyxl (Excel) · ReportLab (PDF) · Pillow (image handling)

---

## Project Structure

```
bhel_pms/
├── app/
│   ├── __init__.py            # Application factory
│   ├── extensions.py          # db, login_manager, bcrypt, migrate instances
│   ├── models/                # SQLAlchemy models (one concern per file)
│   │   ├── user.py            # User + Role constants
│   │   ├── project.py         # Project + ProjectStatus
│   │   ├── hierarchy.py       # Unit, Area, System
│   │   ├── equipment.py       # EquipmentCategory, Equipment, EquipmentStatus
│   │   ├── vendor.py          # Vendor
│   │   ├── progress.py        # DailyProgress, WeeklyProgress, MonthlyProgress
│   │   ├── documents.py       # Photo, Document, Drawing
│   │   ├── notification.py    # Notification
│   │   └── audit.py           # AuditLog
│   ├── routes/                # Flask Blueprints (thin controllers)
│   │   ├── auth.py, dashboard.py, projects.py, units.py, areas.py,
│   │   │   systems.py, equipment.py, vendors.py, progress.py,
│   │   │   reports.py, admin.py, api.py
│   ├── services/               # Business logic layer
│   │   ├── excel_service.py    # Import / export
│   │   ├── pdf_service.py      # PDF report generation
│   │   ├── notification_service.py
│   │   ├── audit_service.py
│   │   └── dashboard_service.py
│   ├── forms/                  # Flask-WTF form definitions + validation
│   ├── utils/                  # decorators (RBAC), validators, helpers
│   ├── templates/               # Jinja2 templates (base + per-module folders)
│   └── static/
│       ├── css/style.css        # Industrial theme (SAP-style sidebar)
│       ├── js/main.js           # Sidebar, notifications, DataTables init
│       ├── js/dashboard.js      # Chart.js dashboard widgets
│       └── uploads/             # photos/ documents/ drawings/
├── config.py                    # Environment based configuration
├── requirements.txt
├── seed.py                      # Demo data seeding script
├── run.py                       # Local dev entry point
├── .env.example
└── README.md
```

---

## Getting Started

### 1. Clone & create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# edit .env and set SECRET_KEY / DATABASE_URL as needed
```

By default, `APP_ENV=development` uses a local SQLite database at
`instance/bhel_pms_dev.db` — no PostgreSQL setup is required to try the app.

### 3. Initialize the database

**Option A — quick start with demo data (recommended for evaluation):**

```bash
python seed.py
```

This drops and recreates all tables, then loads two sample projects
(NTPC Darlipali STPP & Kudankulam NPP) with a full Unit → Area → System →
Equipment hierarchy, vendors, equipment categories, users and progress logs.

**Option B — Flask-Migrate managed schema:**

```bash
flask --app run.py db init
flask --app run.py db migrate -m "Initial schema"
flask --app run.py db upgrade
```

### 4. Run the application

```bash
python run.py
```

Visit **http://localhost:5000** and sign in with a seeded account:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Engineer | `engineer1` | `Engineer@123` |
| Viewer | `viewer` | `Viewer@123` |

---

## Role Permissions

| Capability | Admin | Engineer | Viewer |
|---|:---:|:---:|:---:|
| View dashboard, projects, equipment, reports | ✅ | ✅ | ✅ |
| Create / edit / delete master data & progress logs | ✅ | ✅ | ❌ |
| Upload photos / documents / drawings | ✅ | ✅ | ❌ |
| Excel import | ✅ | ✅ | ❌ |
| User management & audit logs | ✅ | ❌ | ❌ |

---

## Production Deployment Notes

- Set `APP_ENV=production` and supply a PostgreSQL `DATABASE_URL`.
- Serve via a WSGI server: `gunicorn -w 4 -b 0.0.0.0:8000 "run:app"`
- Put a reverse proxy (Nginx) in front for TLS termination and static file caching.
- Ensure `app/static/uploads/` is on persistent storage (or migrate to S3 / Azure Blob for multi-instance deployments).
- Rotate `SECRET_KEY` and store credentials via environment variables / secrets manager — never commit `.env`.

---

## License

Internal tooling reference implementation prepared for demonstration purposes.
