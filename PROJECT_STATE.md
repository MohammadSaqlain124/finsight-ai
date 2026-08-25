# FinSight AI — Project State

**Purpose of this file:** A complete handoff snapshot so a new chat can continue building without re-explaining anything. Read this top to bottom before starting.

---

## 1. What this project is

**FinSight AI** — an AI-powered personal finance analyzer. Final-year B.Tech CSE capstone project. Users upload bank statements (CSV for now; XLSX/PDF planned), and the system extracts, cleans, categorizes, and analyzes transactions to produce financial insights (summaries, monthly comparisons, subscription detection, anomaly detection, and more to come).

**The project must be viva-defensible** — understanding the *why* behind each technical decision matters as much as the code. Build incrementally, explain reasoning, test before every commit.

- **GitHub:** github.com/MohammadSaqlain124/finsight-ai
- **Developer:** Sam (Mohd Saqlain Hussain), 3rd-year CSE, Invertis University
- **Environment:** Windows, Python 3.13.7, VS Code, PowerShell, venv at `E:\Projects\finsight-ai\backend\venv`

---

## 2. How we work together (important — keep this style)

- **Guided build, NOT code dumps.** Walk Sam through each component step by step with reasoning. No downloadable zips of the whole thing. He builds it himself and understands every line.
- **Test before commit.** Every commit is verified working first. Never commit untested code (this is a firm rule — a viva repo where every commit works is the whole point).
- **Read the response body, not just the status code.** Several real bugs returned HTTP 200 with wrong data. Always verify the actual values, ideally by hand-reconciling against known test data.
- **One step at a time.** Sam prefers not to be overwhelmed; incremental progress with a verify step and a commit after each.
- **Pacing matters.** Sam has an L5-S1 disc condition (post-surgery) and has had low-energy / migraine days. Suggest breaks; don't push for commit-count over quality.
- **Grammar corrections** on Sam's messages are welcome, brief.
- Commits double as a GitHub-streak habit — but quality over count, always.

---

## 3. Tech stack (as built)

**Backend (complete for phases 1-5):**
- FastAPI (with `fastapi[standard]`, run via `fastapi dev app/main.py`)
- SQLAlchemy 2.0 ORM, SQLite dev DB (`finsight.db`), `DATABASE_URL` designed to swap to PostgreSQL later
- Pydantic v2 + pydantic-settings (config from `.env`)
- bcrypt (password hashing, direct library), PyJWT (JWT auth)
- pandas (CSV parsing + cleaning)
- python-multipart (form/upload support)

**Frontend (NOT STARTED — this is next):**
- Planned: React via **Vite**, talking to the FastAPI backend
- Spec wants: React, Chart.js/Recharts, responsive dashboard

**Auth model:** JWT bearer tokens. `OAuth2PasswordRequestForm` login (username field = email). Token `sub` = user id. Protected routes use a `get_current_user` dependency.

---

## 4. Project structure (backend)

```
finsight-ai/
├── .gitignore              # ignores venv/, __pycache__/, .env, *.db, uploads/
├── README.md               # project overview, architecture, setup, security
└── backend/
    ├── .env                # SECRET_KEY (64-hex), token expiry — git-ignored
    ├── finsight.db         # SQLite — git-ignored
    ├── uploads/            # UUID-named uploaded files — git-ignored
    └── app/
        ├── __init__.py
        ├── main.py         # FastAPI app, CORS, create_all, includes all routers
        ├── core/
        │   ├── config.py       # Settings (SECRET_KEY, token expiry, UPLOAD_DIR, MAX_UPLOAD_MB)
        │   └── security.py     # hash_password, verify_password, create_access_token, decode_access_token
        ├── db/
        │   ├── base.py         # Base (DeclarativeBase)
        │   └── session.py      # engine, SessionLocal, get_db()
        ├── models/
        │   ├── user.py         # User
        │   ├── statement.py    # Statement
        │   ├── transaction.py  # Transaction
        │   └── subscription.py # Subscription
        ├── schemas/
        │   ├── user.py         # UserCreate, UserRead
        │   ├── token.py        # Token
        │   ├── statement.py    # StatementRead
        │   ├── transaction.py  # TransactionRead
        │   └── subscription.py # SubscriptionRead
        ├── services/
        │   ├── csv_parser.py    # parse_csv — column-alias normalization, NaN-safe
        │   ├── cleaner.py       # clean_transactions — dates, amounts, income/expense
        │   ├── categorizer.py   # categorize — rule-based + confidence
        │   ├── analytics.py     # summarize, summarize_by_month, compare_last_two_months
        │   ├── subscriptions.py # detect_subscriptions
        │   └── anomalies.py     # detect_anomalies (zscore + iqr)
        └── api/
            ├── deps.py          # get_current_user (token -> User)
            └── routers/
                ├── auth.py        # /api/auth/register, /login
                ├── users.py       # /api/users/me
                ├── statements.py  # upload, list, preview, confirm, transactions, categorize
                └── analytics.py   # summary, monthly, comparison, subscriptions(+detect/saved/dismiss), anomalies
```

---

## 5. Data models (current schema)

**User:** id, email (unique), full_name, hashed_password, is_active, created_at

**Statement:** id, user_id (FK), original_filename, stored_filename (UUID name on disk), file_type, status (uploaded → processed), uploaded_at

**Transaction:** id, user_id (FK), statement_id (FK), date (real Date), description, amount (float, positive magnitude), transaction_type (income/expense), category (default "Uncategorized"), balance (nullable), created_at

**Subscription:** id, user_id (FK), merchant, average_amount, frequency, occurrences, estimated_annual_cost, confidence, last_payment, user_dismissed (bool, soft-dismiss), detected_at

---

## 6. API endpoints (all working & tested)

**Auth**
- `POST /api/auth/register` → create user (201)
- `POST /api/auth/login` → JWT token (form: username=email, password)
- `GET /api/users/me` → current user (protected)

**Statements / pipeline**
- `POST /api/statements/upload` → validate + save file (UUID rename), status "uploaded"
- `GET /api/statements` → list user's statements
- `GET /api/statements/{id}/preview` → parse + clean, show transactions (not stored)
- `POST /api/statements/{id}/confirm` → store transactions, auto-categorize, dedup guard, status "processed"
- `GET /api/statements/{id}/transactions` → stored transactions for a statement
- `POST /api/statements/{id}/categorize` → re-categorize stored transactions

**Analytics**
- `GET /api/analytics/summary` → totals, savings rate, category breakdown, biggest expense
- `GET /api/analytics/monthly` → per-month breakdown (grouped by YYYY-MM)
- `GET /api/analytics/comparison` → last-two-months comparison + "what_changed" English insights
- `GET /api/analytics/subscriptions` → live detection (not stored)
- `POST /api/analytics/subscriptions/detect` → detect + STORE (respects dismissals, no dupes)
- `GET /api/analytics/subscriptions/saved?include_dismissed=false` → stored subs
- `PATCH /api/analytics/subscriptions/{id}/dismiss` → soft-dismiss a subscription
- `GET /api/analytics/anomalies?method=zscore|iqr` → unusual-transaction detection

---

## 7. Phase progress

- **Phase 1 — DONE:** FastAPI setup, DB engine, User model, bcrypt hashing, JWT auth, protected /me
- **Phase 2 — DONE:** Secure upload (UUID rename, validation), CSV parsing (column aliases), cleaning (dates/amounts/income-expense), preview-then-confirm, persist transactions, content-based duplicate guard
- **Phase 3 — DONE:** Rule-based categorization + confidence scores + explainability; auto-categorize on import
- **Phase 4 — DONE:** Financial summary; per-month grouping; month-vs-month comparison with % change, direction, and "What Changed?" insights
- **Phase 5 — DONE:** Subscription detection (interval rhythm + amount-consistency, false-positive rejection); persistent storage with soft-dismiss + dismissal-aware re-detection; anomaly detection (z-score AND IQR, user-selectable, explainable reasons)

**~12 commits pushed. Backend analysis engine is complete.**

**NOT built yet:** XLSX/PDF parsing, financial health score, budget recommendations, financial goals, cash-flow prediction, AI summary/NL assistant, export, tests, **and the entire frontend.**

---

## 8. Key learnings / bugs caught (viva-worthy — remember these)

- **NaN → JSON crash:** pandas empty cells become NaN, which isn't valid JSON → 500 on serialize. Fixed by sanitizing to None *after* leaving the DataFrame (pandas float columns coerce None back to NaN, so `.where()` inside the DF didn't work).
- **dayfirst date-swap:** `dayfirst=True` wrongly swapped ISO dates (2026-08-01 → Jan 8). Fixed by detecting ISO format via regex and only applying dayfirst to non-ISO dates.
- **Subscription false positives (two rounds):** 2-occurrence merchants and inconsistent amounts got flagged. Fixed by requiring 3+ occurrences AND a coefficient-of-variation (amount consistency) check.
- **Duplicate data pollution (hit 3x):** re-importing the same statement doubled transactions, wrecking analytics/subscriptions. Fixed with a content-based duplicate guard (skip if same user+date+description+amount already exists).
- **z-score vs IQR insight:** on data with one extreme outlier, z-score flagged fewer anomalies because the outlier inflates the mean/std (hiding smaller anomalies), while IQR (median-based) stayed robust. Good to explain in viva.
- **General:** always stop the server before deleting finsight.db (Windows file lock). After deleting the DB, re-register + re-authorize (old JWT points to a now-nonexistent user → 401).

---

## 9. Test data files used (in backend/, recreate as needed)

Sam has been testing with small CSVs using varied headers (Txn Date/Narration/Withdrawal/Deposit/Balance) to exercise the column-alias mapping, plus multi-month files for comparison, a subs.csv (NETFLIX/SPOTIFY ×3 monthly) for subscription detection, and an anomaly_test.csv (normal spends + one ₹75,000 laptop outlier) for anomaly detection.

---

## 10. NEXT UP → FRONTEND (React + Vite)

This is the immediate task in the new chat. See the accompanying prompt. Key constraints:
- **Full React app via Vite**, talking to the FastAPI backend.
- **The UI must NOT look like a generic AI-generated site** (no default purple gradients / glassmorphism / Inter-everywhere / center-everything template look). Sam will provide reference design images for inspiration (analyze for direction, don't copy).
- Follow the same guided, incremental, test-before-commit approach.
- Likely first slices: Vite setup + CORS, auth pages (login/register), then the dashboard consuming /api/analytics/summary.
