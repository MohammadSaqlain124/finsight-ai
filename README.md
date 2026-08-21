# FinSight AI

An AI-powered personal finance analyzer that turns raw bank statements into
meaningful financial insights. Final-year B.Tech CSE project.

## Features (implemented so far)

- **Secure authentication** — registration and login with bcrypt password
  hashing and JWT-based sessions. User data is fully isolated.
- **Statement upload** — CSV upload with validation (type, size, empty-file
  checks) and safe UUID-based file storage (path-traversal defense).
- **Transaction extraction** — CSV parsing with a column-alias normalization
  layer that maps diverse bank header formats to a common schema.
- **Data cleaning** — handles multiple date formats, currency symbols,
  comma-separated amounts, empty cells, and unparseable rows.
- **Preview-then-confirm import** — users preview extracted transactions before
  they are permanently stored.
- **Rule-based categorization** — merchant-keyword matching with confidence
  scores and explainability (e.g. "Food & Dining because it matched 'swiggy'").

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite (development), SQLAlchemy ORM
- **Data processing:** pandas
- **Auth:** JWT (PyJWT), bcrypt
- **Planned:** PostgreSQL (production), React frontend, ML categorization

## Architecture

The backend follows a layered design where routers stay thin and services do
the work:

- `core/` — configuration and security (JWT, password hashing)
- `db/` — database engine, session management, base model
- `models/` — SQLAlchemy ORM models (User, Statement, Transaction)
- `schemas/` — Pydantic request/response contracts
- `services/` — parsing, cleaning, categorization, analytics logic
- `api/routers/` — HTTP endpoints

Data flows through a pipeline:
`Upload → Parse → Clean → Categorize → Store → Analyze`

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install fastapi[standard] sqlalchemy pandas bcrypt pyjwt pydantic[email] python-multipart
fastapi dev app/main.py
```

Then open http://127.0.0.1:8000/docs for the interactive API documentation.

## Security

- Passwords are never stored in plain text (bcrypt hashing).
- Uploaded files are stored under randomized names, never the user's filename.
- Every data query is scoped to the authenticated user.
- Secrets (JWT signing key) are kept in a git-ignored `.env` file.

## Status

Phases 1–3 complete: authentication, file upload, transaction extraction and
cleaning, and rule-based categorization. Analytics, dashboard, and additional
file formats (XLSX, PDF) are in progress.