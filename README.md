# SyncMind AI — Meeting Notes & Action Tracker

[![Django](https://img.shields.io/badge/Django-4.2+-092e20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14+-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![AI-Powered](https://img.shields.io/badge/AI-Gemini%20%7C%20OpenAI%20%7C%20Mock-blue?style=for-the-badge&logo=openai&logoColor=white)](https://ai.google.dev/)
[![MySQL Ready](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)

A modern, full-stack **AI Meeting Notes & Action Tracker** built for the Zignuts assessment. SyncMind AI transforms raw meeting transcripts into executive summaries, discussion points, key decisions, risks, unanswered questions, and structured action items with deadline tracking and overdue alerts.

---

## 🚀 Key Features & Workflow

```
Register / Login
       │
       ▼
Executive Dashboard  ◄─────── Real-time Metrics & Overdue Alerts
       │
       ▼
Create / Upload Meeting ────► Rich Text (Quill.js) or .TXT file drag & drop
       │
       ▼
Generate AI Insights ───────► Hybrid Gemini / OpenAI / Mock AI
       │
       ├─► Executive Summary
       ├─► Discussion Points & Key Decisions
       ├─► Risks, Blockers & Unanswered Questions
       └─► Action Deliverables (Task, Owner, Due Date, Priority)
       │
       ▼
Extract to Central Action Tracker ──► Live Search, Filters, Overdue Badges & Inline Status Updates
```

### 1. 🔐 Authentication & Data Isolation
- User Registration, Login, Logout with form validations and secure password hashing.
- Strict multi-tenancy: every meeting, transcript, and action item is isolated to the authenticated user.

### 2. 📝 Meeting Management & Rich Transcripts
- Full CRUD for meetings with Title, Date, Meeting Type (Sprint, Standup, Client, 1-on-1, Board, General), Participants, and Transcript.
- **Quill.js Rich Text Editor** with live character & word counting.
- **.TXT File Drag & Drop** dropzone with instant client-side decoding.
- 1-Click **Sample Demo Transcripts** (Sprint Planning, Client Review).
- Fast search & multi-type filtering.

### 3. 🤖 AI Intelligence Engine (Gemini / OpenAI / Structured Mock)
- **Zero-Hallucination Constraints**: extracts only grounded information.
- **Automated Fallbacks**: Missing owner $\rightarrow$ `"Unassigned"`, missing due date $\rightarrow$ `"Not specified"`.
- **Hybrid AI Client**:
  - Google Gemini API (`GEMINI_API_KEY`)
  - OpenAI API (`OPENAI_API_KEY`)
  - High-fidelity **Contextual Mock AI** fallback that dynamically parses meeting text when no key is supplied, ensuring the platform is **100% demonstrable offline**.
- **Interactive UI**: Animated step progress bar + smooth reveal + 1-click single or bulk action item extraction to database.

### 4. ⚡ Central Action Tracker
- Centralized tracking board across all meetings.
- Live debounced search by task, owner, or meeting title.
- Multi-filter toolbar: Status (`Open`, `In Progress`, `Blocked`, `Completed`), Priority (`High`, `Medium`, `Low`), Assignee dropdown, Due Date range, Overdue only toggle.
- **Inline AJAX Status Switcher**: cycle status without reloading the page.
- Overdue badge indicators with pulse glow for tasks past deadline.
- Export to **CSV** spreadsheet.

### 5. 📊 Executive Analytics Dashboard
- Animated metric cards: Total Meetings, Total Actions, Open, In Progress, Completed, Overdue.
- Dynamic completion rate progress ring.
- Recent Meetings feed with action count badges.
- Urgent / Overdue Actions quick list.

### 6. 🎨 Polished Modern SaaS UI/UX
- **Design System**: Indigo/Purple/Teal gradient aesthetic with soft shadows and rounded surfaces.
- **Dark Mode & Light Mode**: Built-in toggle persisted in `localStorage` with system preference detection.
- **Micro-Animations**: Staggered card entrances, hover lift effects, shimmer loaders, and `@media (prefers-reduced-motion: reduce)` accessibility support.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons 1.11, Vanilla JavaScript, Quill.js |
| **Backend** | Python 3.9+, Django 4.2 LTS, Django REST Framework (DRF) |
| **Database** | MySQL (with PyMySQL driver) / SQLite auto-fallback |
| **AI Integration** | Google Gemini (`google-generativeai`), OpenAI API, Contextual Mock AI |

---

## 📂 Project Architecture

```
Zignuts_project_demo/
├── core/                         # Django project configuration
│   ├── settings.py               # MySQL/SQLite, Auth, DRF & AI config
│   ├── urls.py                   # Master routing
│   └── views.py                  # Dashboard & Error handlers
├── accounts/                     # User Auth & Profile management
├── meetings/                     # Meeting CRUD, Quill editor, TXT import
│   ├── models.py                 # Meeting & MeetingInsight models
│   └── management/commands/      # seed_demo_data command
├── actions/                      # Central Action Tracker & Status API
│   ├── models.py                 # ActionItem model with is_overdue property
│   └── views.py                  # Action tracker filters & CSV export
├── ai_service/                   # AI Orchestrator & Validators
│   ├── client.py                 # Gemini / OpenAI / Mock AI caller
│   ├── mock_ai.py                # Contextual natural language extractor
│   ├── prompts.py                # System schemas & rules
│   └── validators.py             # Strict output sanitizer
├── api/                          # REST API Endpoints & Serializers
├── templates/                    # Semantic HTML5 Templates (Light/Dark)
│   ├── base.html                 # Master layout with navbar, toasts, modals
│   ├── dashboard.html            # Analytics dashboard
│   ├── accounts/                 # Login, Register, Profile
│   ├── meetings/                 # List, Form (Quill), Detail (AI Insights)
│   └── actions/                  # Action Tracker table & modals
├── static/                       # Static Assets
│   ├── css/                      # theme.css, animations.css, main.css
│   └── js/                       # theme.js, main.js, animations.js, meeting_editor.js, action_tracker.js
├── .env.example                  # Environment configuration template
├── requirements.txt              # Production dependencies
├── manage.py
└── README.md
```

---

## ⚙️ Quick Start Installation Guide

### 1. Clone & Setup Virtual Environment

```bash
cd /path/to/Zignuts_project_demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to configure your database and optional AI API keys:

```ini
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings (MySQL or SQLite)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=ai_meeting_tracker
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306

# AI Keys (Optional - uses built-in Mock AI if omitted)
GEMINI_API_KEY=
OPENAI_API_KEY=
AI_PROVIDER=auto
```

### 3. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Demo Data (Optional but Recommended)

Populate sample meetings, AI insights, and action items:

```bash
python manage.py seed_demo_data
```

**Demo Credentials created:**
- **Username:** `demo`
- **Password:** `demo_password_2026`

### 5. Run the Local Development Server

```bash
python manage.py runserver 127.0.0.1:8000
```

Open your browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Running Automated Tests

Run the complete test suite:

```bash
python manage.py test
```

All 22 unit & integration tests covering Authentication, Meeting CRUD, Action Items, AI schema validation, and REST APIs will run.

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/meetings/` | List user's meetings (supports `?q=`, `?type=`) |
| `POST` | `/api/meetings/` | Create a new meeting |
| `GET` | `/api/meetings/<id>/` | Retrieve meeting details with insights & action items |
| `GET` | `/api/actions/` | List action items with filters (`?status=`, `?priority=`, `?owner=`, `?overdue=true`) |
| `POST` | `/api/actions/` | Create an action item |
| `PATCH` | `/api/actions/<id>/status/` | Update action status inline |
| `POST` | `/api/ai/generate/` | Trigger AI insights generation for a meeting |
| `POST` | `/api/ai/extract-actions/` | Bulk-extract AI action items into database |
| `GET` | `/api/dashboard/stats/` | Fetch live dashboard metrics |

---

## 🛡️ Security & Quality Standards

- **CSRF Protection**: All POST/PUT/DELETE forms & AJAX endpoints include valid CSRF tokens.
- **Data Isolation**: User querysets strictly filtered by `request.user`.
- **Validation**: Server-side and client-side validation on forms and JSON payloads.
- **SQL Injection & XSS Protection**: Django ORM parameterized queries and template auto-escaping.
- **Sanitized Uploads**: File extension and size constraints on `.txt` file uploads.

---

## 📄 License & Attribution

Built for the **Zignuts TechnoLab Full-Stack Assessment**.
Developed with precision by the candidate.
