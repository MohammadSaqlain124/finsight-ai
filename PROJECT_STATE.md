# FinSight AI — Project State

FinSight AI is an AI-assisted personal finance analyzer built as a final-year B.Tech Computer Science capstone project. Users upload their bank statements; the application extracts, cleans, categorizes, and analyzes the transactions to surface practical financial insight — spending summaries, month-over-month comparisons, recurring-subscription detection, and anomaly detection — through a clean web dashboard.

The project is built to be understood, not merely to run. Each significant technical decision is deliberate and documented, so the architecture can be explained and defended in depth.

- **Repository:** github.com/MohammadSaqlain124/finsight-ai
- **Author:** Mohd Saqlain Hussain — B.Tech CSE, Invertis University
- **Status:** Backend analysis engine complete. Frontend authentication and application shell complete; data dashboard and responsive layout in progress.

---

## Tech stack

**Backend**
- FastAPI (Python) — REST API
- SQLAlchemy 2.0 ORM with SQLite for development (schema designed to migrate to PostgreSQL)
- Pydantic v2 and pydantic-settings for validation and configuration
- JWT authentication (PyJWT) with bcrypt password hashing
- pandas for statement parsing and cleaning

**Frontend**
- React, built with Vite
- react-router-dom for client-side routing
- Plain CSS using CSS custom properties (design tokens) and CSS Modules for component-scoped styling — deliberately no UI framework, to keep full control over a bespoke visual identity
- IBM Plex type family (Serif for display, Sans for UI, Mono for financial figures)

**Authentication model:** JWT bearer tokens. Login uses the OAuth2 password flow; the signed token is stored in the browser and attached to every authenticated request. Protected API routes resolve the current user through a FastAPI dependency; protected frontend routes are guarded by a route wrapper that redirects unauthenticated users to the sign-in page.

---

## Architecture at a glance

A React single-page application (served by Vite in development) communicates over HTTP with the FastAPI backend, which persists data in SQLite. After login, the browser holds a signed JWT and sends it as a bearer token on every authenticated request; the backend validates the token and scopes all data to the authenticated user. Cross-origin requests between the development frontend and backend are permitted by CORS middleware.

```
React SPA (Vite, :5173)  ──HTTP + JWT──▶  FastAPI (:8000)  ──▶  SQLite
```

---

## Features implemented

**Authentication and users**
- Registration with bcrypt-hashed passwords, login that issues a JWT, and a protected "current user" endpoint.
- Frontend: styled sign-in and registration pages, token persistence, automatically attached bearer authentication, a protected dashboard, session restoration on page refresh, and sign-out.

**Statement pipeline**
- Secure file upload with UUID-based storage and validation.
- CSV parsing with column-alias normalization, so statements from different banks with different header names are understood.
- Data cleaning covering multi-format dates, currency symbols, thousands separators, and empty cells.
- A preview-then-confirm import flow, with a content-based duplicate guard that prevents the same statement being imported twice.

**Categorization**
- Rule-based transaction categorization with confidence scores and keyword-level explainability, applied automatically on import.

**Analytics**
- Financial summary: income, expenses, savings rate, category breakdown, and largest expense.
- Per-month breakdown and month-over-month comparison, including plain-English "what changed" insights.

**Recurring payments**
- Subscription detection using interval-rhythm and amount-consistency analysis, with database persistence, a soft-dismiss capability, and dismissal-aware re-detection.

**Anomaly detection**
- Unusual-transaction detection offered through two user-selectable methods — z-score and interquartile range (IQR) — each returning a human-readable reason.

**Design system — "Modern Ledger"**
- A deliberate visual identity grounded in bookkeeping: a cool "ledger paper" background rather than plain white, ink-black and ledger-red semantics ("in the black" / "in the red"), and monospaced tabular figures so financial numbers align in columns like a real statement.
- Reusable, accessible components (button, text field, authentication layout) built on a CSS custom-property token system, so the entire theme can be adjusted from one place.

---

## Project structure

**Backend**

```
backend/
├── .env                    # secret key, token settings (git-ignored)
├── finsight.db             # SQLite database (git-ignored)
├── uploads/                # UUID-named uploaded files (git-ignored)
└── app/
    ├── main.py             # app setup, CORS, router registration
    ├── core/               # configuration and security (hashing, JWT)
    ├── db/                 # engine, session, base
    ├── models/             # User, Statement, Transaction, Subscription
    ├── schemas/            # Pydantic request/response models
    ├── services/           # parsing, cleaning, categorization, analytics,
    │                       #   subscriptions, anomalies
    └── api/
        ├── deps.py         # current-user dependency
        └── routers/        # auth, users, statements, analytics
```

**Frontend**

```
frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx            # entry — BrowserRouter + AuthProvider
    ├── App.jsx             # route table
    ├── index.css           # design tokens and base styles
    ├── context/
    │   └── AuthContext.jsx     # global auth state (user, login, logout)
    ├── lib/
    │   ├── api.js              # fetch wrapper: JSON + form bodies, bearer auth, errors
    │   └── auth.js             # token storage helpers
    ├── components/
    │   ├── Button.jsx  (+ .module.css)
    │   ├── TextField.jsx  (+ .module.css)
    │   ├── AuthLayout.jsx  (+ .module.css)
    │   └── ProtectedRoute.jsx
    └── pages/
        ├── Login.jsx
        ├── Register.jsx
        └── Dashboard.jsx
```

---

## Data models

- **User:** id, email (unique), full name, hashed password, active flag, created-at.
- **Statement:** id, owner, original filename, stored (UUID) filename, file type, status (uploaded → processed), uploaded-at.
- **Transaction:** id, owner, statement, date, description, amount (positive magnitude), type (income / expense), category, balance (optional), created-at.
- **Subscription:** id, owner, merchant, average amount, frequency, occurrences, estimated annual cost, confidence, last payment, dismissed flag, detected-at.

---

## API endpoints

**Authentication**
- `POST /api/auth/register` — create a user
- `POST /api/auth/login` — obtain a JWT (OAuth2 password flow)
- `GET /api/users/me` — current user (protected)

**Statements and pipeline**
- `POST /api/statements/upload` — validate and store an uploaded file
- `GET /api/statements` — list the user's statements
- `GET /api/statements/{id}/preview` — parse and clean, without storing
- `POST /api/statements/{id}/confirm` — store transactions, auto-categorize, de-duplicate
- `GET /api/statements/{id}/transactions` — stored transactions for a statement
- `POST /api/statements/{id}/categorize` — re-categorize stored transactions

**Analytics**
- `GET /api/analytics/summary` — totals, savings rate, category breakdown, biggest expense
- `GET /api/analytics/monthly` — per-month breakdown
- `GET /api/analytics/comparison` — last-two-months comparison with insights
- `GET /api/analytics/subscriptions` — live detection
- `POST /api/analytics/subscriptions/detect` — detect and store
- `GET /api/analytics/subscriptions/saved` — stored subscriptions
- `PATCH /api/analytics/subscriptions/{id}/dismiss` — soft-dismiss a subscription
- `GET /api/analytics/anomalies?method=zscore|iqr` — unusual-transaction detection

---

## Notable engineering decisions and problems solved

- **NaN and JSON serialization.** Empty cells become `NaN` in pandas, which is not valid JSON and caused serialization failures. Because pandas can silently coerce `None` back to `NaN` inside a float column, values are sanitized to `None` only *after* leaving the DataFrame.
- **Ambiguous date parsing.** Applying day-first parsing globally corrupted ISO dates (e.g. `2026-08-01` read as 8 January). ISO-formatted dates are now detected first, and day-first interpretation is applied only to non-ISO input.
- **Subscription false positives.** Early detection flagged coincidental repeats. Detection now requires a minimum number of occurrences and an amount-consistency check (coefficient of variation) before a merchant is treated as recurring.
- **Duplicate data pollution.** Re-importing a statement previously doubled transactions and skewed analytics. A content-based duplicate guard now skips any transaction matching an existing owner, date, description, and amount.
- **Robustness of anomaly methods.** A single extreme outlier inflates the mean and standard deviation, which can hide smaller anomalies from the z-score method; the median-based IQR method stays robust. Offering both, side by side, makes the trade-off explicit.
- **Cross-origin access.** The browser blocks responses between the frontend (`:5173`) and backend (`:8000`) as different origins; CORS middleware on the backend grants access to the specific development origin, rather than using a permissive wildcard.
- **Login content type.** The OAuth2 password flow expects form-encoded data with a `username` field, not JSON, so the API client sends the two request styles appropriately.
- **Token storage trade-off.** The JWT is stored in `localStorage` for simplicity; this is readable by JavaScript and therefore exposed to XSS, whereas an httpOnly cookie with CSRF protection is the more secure production choice. The trade-off is understood and documented rather than accidental.

**Working practices.** Development proceeds in small, independently verifiable steps; each commit is confirmed working before it is pushed, so every point in the history builds and runs. Behaviour is verified against actual response data, not only HTTP status codes, and previously passing cases are re-checked after each change.

---

## Running locally

Both servers run together during development.

**Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
# create .env with SECRET_KEY and token settings
fastapi dev app/main.py          # serves on http://localhost:8000
```

**Frontend**
```
cd frontend
npm install
npm run dev                      # serves on http://localhost:5173
```

---

## Roadmap

- **Responsive layout** for the authentication pages and dashboard (mobile and tablet).
- **Data dashboard** consuming the analytics endpoints — summary figures, category breakdown, monthly trends, subscriptions, and anomalies — rendered in the Modern Ledger style.
- **Refined visual identity** — a marble brand panel; the art direction is chosen, with a license-clear asset to be finalized.
- **Additional backend capabilities** — XLSX and PDF statement parsing, a financial health score, budget recommendations, savings goals, cash-flow prediction, natural-language summaries, and data export.
- **Automated testing.**
