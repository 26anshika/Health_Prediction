# Health Prediction Application

A full-stack **web application** for managing patient contact records and generating **AI-assisted health screening remarks** from blood test results. Built as part of an **AI/ML skills evaluation** task: it demonstrates CRUD operations, data validation, persistent storage, external API integration, and a clean user interface.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Configuration & Security](#configuration--security)
- [API Integration](#api-integration)
- [Data Model](#data-model)
- [Validation Rules](#validation-rules)
- [Assessment Criteria Mapping](#assessment-criteria-mapping)
- [Demo Video & Submission](#demo-video--submission)
- [Documentation](#documentation)
- [Disclaimer](#disclaimer)

---

## Overview

Healthcare staff or administrators can use this application to:

1. **Store** patient contact details and lab values (glucose, haemoglobin, cholesterol).
2. **Automatically generate** plain-language health assessment remarks using clinical reference ranges and external health/ML APIs.
3. **Manage** records through full **Create, Read, Update, and Delete (CRUD)** operations via a browser-based dashboard.

The solution is intentionally scoped as a **screening aid** — not a medical diagnosis tool. All generated remarks include a clear disclaimer directing users to qualified healthcare professionals.

---

## Key Features

| Feature | Description |
|--------|-------------|
| **CRUD operations** | Add, list, view, edit, and delete patient records |
| **Patient fields** | Full name, date of birth, email, glucose, haemoglobin, cholesterol, AI-generated remarks |
| **Input validation** | Valid email format, DOB not in the future, numeric non-negative lab values |
| **Persistent storage** | SQLite database via SQLAlchemy (file: `instance/health_prediction.db`) |
| **AI/ML remarks** | Structured health assessment on create/update (overall risk, per-marker explanation, suggested actions) |
| **Responsive UI** | Bootstrap 5, Bootstrap Icons, custom CSS, health-themed imagery |
| **Secure config** | Secrets via environment variables; `.env` excluded from Git |

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | Python 3.10+, Flask 3 | Lightweight, fast to develop, well-suited for assessment CRUD + API calls |
| **ORM / DB** | Flask-SQLAlchemy, SQLite | Zero external DB setup; portable for reviewers cloning the repo |
| **Frontend** | Jinja2 templates, Bootstrap 5, Bootstrap Icons | Clean UI without a separate Node build step |
| **HTTP client** | `requests` | External WHO and Hugging Face API calls |
| **Config** | `python-dotenv` | Local `.env` for optional API tokens (not committed) |

**Why not React/Node?** For this assessment, a **server-rendered Flask app** keeps deployment simple (single `python app.py`), reduces repository size, and still satisfies the task requirement for “any frontend technology” including HTML/CSS/Bootstrap.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Bootstrap UI)                   │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP
┌─────────────────────────────▼───────────────────────────────┐
│  Flask (app.py)                                                │
│  ├── Routes: index, create, view, edit, delete                 │
│  ├── validators.py → form validation                           │
│  └── health_service.py → prediction + external APIs            │
└─────────────┬───────────────────────────────┬─────────────────┘
              │                               │
┌─────────────▼──────────────┐   ┌────────────▼────────────────┐
│  SQLite (SQLAlchemy)        │   │  External APIs               │
│  Patient model (models.py)  │   │  • WHO GHO API               │
└────────────────────────────┘   │  • Hugging Face (optional)   │
                                 └──────────────────────────────┘
```

**Request flow (Create/Update):**

1. User submits the patient form.
2. `validators.py` checks email, DOB, and numeric lab fields.
3. `health_service.py` evaluates each marker, calls WHO (and optionally Hugging Face), builds structured remarks.
4. Record is saved to SQLite; user is redirected to the detail view.

---

## Project Structure

```
Health_Prediction/
├── app.py                 # Flask app, routes, app factory
├── config.py              # App configuration (DB URI, API settings)
├── models.py              # Patient SQLAlchemy model
├── validators.py          # Server-side input validation
├── health_service.py      # Health assessment + API integration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template (safe to commit)
├── .gitignore             # Excludes .env, venv, __pycache__, etc.
├── LOCAL_SETUP.md         # Step-by-step local run guide
├── DEMO_VIDEO_SCRIPT.txt  # Script for assessment demo recording
├── README.md              # This file
├── docs/
│   └── screenshots/       # Add dashboard, view, add-patient images here
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html         # Patient dashboard (list)
│   ├── patient_detail.html
│   └── patient_form.html
├── static/
│   └── css/style.css
└── instance/              # SQLite DB (created at runtime, gitignored)
```

---

## Screenshots

Add your UI captures under `docs/screenshots/` and they will render here on GitHub.

### Patient Dashboard (List all records)

<img width="1696" height="897" alt="dashboard" src="https://github.com/user-attachments/assets/beb20172-3932-43ce-879c-bf6d01a27e2b" />


*Main dashboard: patient table, lab values, assessment summary, and CRUD action buttons.*

### View Patient (Detail + Health Assessment)

<img width="1633" height="882" alt="view-patient" src="https://github.com/user-attachments/assets/a31a5b79-5907-4bbe-b8e6-955cf2fdf7ca" />


*Patient profile, colour-coded lab cards, and structured AI health remarks.*

### Add Patient (Create record)

<img width="1672" height="812" alt="add-patient" src="https://github.com/user-attachments/assets/f18da998-c152-49cf-9098-c7dbfa9f3363" />


*Form to enter contact details and blood test values; remarks are generated on save.*

> **Note for submission:** Place your snapshot files as:
> - `docs/screenshots/dashboard.png`
> - `docs/screenshots/view-patient.png`
> - `docs/screenshots/add-patient.png`

---

## Getting Started

### Prerequisites

- Python **3.10+**
- Internet access (for WHO API; optional Hugging Face token)
- Web browser

### Installation

```powershell
cd Health_Prediction
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
copy .env.example .env         # optional: configure HF_API_TOKEN
python app.py
```

Open **http://127.0.0.1:5000**

For full setup, troubleshooting, and sample test data, see **[LOCAL_SETUP.md](LOCAL_SETUP.md)**.

---

## Configuration & Security

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | No (dev default) | Flask session secret — set in production |
| `HF_API_TOKEN` | No | Hugging Face token for enhanced ML zero-shot classification |
| `HF_MODEL` | No | Model ID (default: `facebook/bart-large-mnli`) |
| `DATABASE_URL` | No | Override SQLite path if needed |

**Before pushing to GitHub:**

- Never commit `.env` or real API keys.
- Use `.env.example` only as a template.
- Confirm `.gitignore` includes `.env`, `venv/`, and `instance/*.db` if you do not want DB data in the repo.

---

## API Integration

| API | Purpose | When called |
|-----|---------|-------------|
| **WHO Global Health Observatory (GHO)** | Public-health context for diabetes screening | Every create/update |
| **Hugging Face Inference API** | Optional zero-shot ML confirmation of risk labels | When `HF_API_TOKEN` is set |

**Remarks content includes:**

- Overall risk level (normal / caution / alert)
- Per-marker: result, plain-language meaning, suggested next steps
- WHO health insight
- Optional AI model agreement note
- Medical disclaimer

Implementation: `health_service.py`

---

## Data Model

**Patient** (`models.py`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `full_name` | String | Patient name |
| `date_of_birth` | Date | Used to calculate age for assessment |
| `email` | String | Contact email |
| `glucose` | Float | mg/dL |
| `haemoglobin` | Float | g/dL |
| `cholesterol` | Float | mg/dL |
| `remarks` | Text | AI-generated health assessment |
| `created_at` / `updated_at` | DateTime | Audit timestamps |

---

## Validation Rules

Implemented in `validators.py`:

- **Full name:** Required, max 120 characters
- **Email:** Required, valid format
- **Date of birth:** Required, valid date, **cannot be in the future**
- **Glucose, haemoglobin, cholesterol:** Required, numeric, **≥ 0**

Client-side HTML5 validation is supplemented by server-side checks on every submit.

---

## Assessment Criteria Mapping

| Criterion | How this project addresses it |
|-----------|--------------------------------|
| **Problem-solving approach** | Modular separation: routes, validation, persistence, health/AI logic |
| **Code quality & structure** | Single-responsibility modules, typed helpers, consistent naming |
| **API integration** | WHO GHO + optional Hugging Face; graceful fallback if APIs fail |
| **Frontend & backend** | Flask server-rendered pages + Bootstrap UI with clear UX |
| **GitHub organization** | README, setup guide, demo script, `.gitignore`, `.env.example`, screenshots folder |
| **Clarity & maintainability** | Documented flows, structured remarks format, easy local run |

---

## Demo Video & Submission

When submitting the assessment, provide:

1. **GitHub repository link** (public or shared with assessors)
2. **Demo video** (OBS Studio, Zoom, etc.) covering:
   - CRUD walkthrough via the UI
   - Why this technology stack was chosen
   - Challenges faced during development

A full **spoken script and scene checklist** is in **[DEMO_VIDEO_SCRIPT.txt](DEMO_VIDEO_SCRIPT.txt)**.

---

## Documentation

| File | Purpose |
|------|---------|
| [LOCAL_SETUP.md](LOCAL_SETUP.md) | Install and run locally |
| [DEMO_VIDEO_SCRIPT.txt](DEMO_VIDEO_SCRIPT.txt) | Video recording guide |
| [.env.example](.env.example) | Safe environment variable template |

---

## Disclaimer

This application produces **automated screening remarks** for educational and assessment purposes only. It does **not** replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for clinical decisions.

---

## Author
Anshika Yadav
Assessment submission — Health Prediction Application (AI/ML Skills Evaluation).
