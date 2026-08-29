# FinSight AI, Project State

FinSight AI is an AI assisted personal finance analyzer, built as my final year B.Tech Computer Science project. You give it a bank statement, a CSV or a PDF including password protected ones, and it pulls out the transactions, cleans them, strips out sensitive details, categorizes them, and analyzes them. The results show up on a dashboard.

I've tried to build it so every decision has a reason I can actually explain, rather than something that just happens to work.

Repository: github.com/MohammadSaqlain124/finsight-ai
Author: Mohd Saqlain Hussain, B.Tech CSE, Invertis University

Status: the backend analysis engine is finished, and so is the frontend. Authentication, statement upload for both CSV and PDF, and the full analytics dashboard are all built, styled, and working end to end.

## Tech stack

The backend runs on FastAPI. Data lives in SQLite through the SQLAlchemy ORM, and the schema is written so a move to PostgreSQL later wouldn't mean rewriting queries. Validation and config use Pydantic and pydantic-settings. Auth is JWT with PyJWT and bcrypt. pandas does the CSV parsing and cleaning, and PDF work is handled by pdfplumber for extraction and pikepdf for decrypting locked files.

The frontend is React built with Vite, using react-router-dom for routing. Styling is plain CSS with design tokens and CSS Modules instead of a UI framework, which was a deliberate choice to keep control over the visual identity. Type is the IBM Plex family, serif for headings, sans for the interface, and mono for the numbers.

On auth, the app uses JWT bearer tokens. Login goes through the OAuth2 password flow and is rate limited against brute force. The signed token sits in the browser and rides along on every authenticated request. On the backend, protected routes resolve the current user through a dependency, and on the frontend a route wrapper sends anyone without a valid token back to the login page.

## How it fits together

The React app talks to the FastAPI backend over HTTP, and FastAPI stores everything in SQLite. Once you log in, the browser holds a signed JWT and sends it as a bearer token with each request. The backend checks the token and scopes every query to that user, so nobody can read anyone else's data. CORS is set to allow only the frontend origin during development.

## What's built

Auth and users. Registration hashes the password with bcrypt, login hands back a JWT, and there is a protected endpoint for the current user. Repeated failed logins from one client get throttled with a sliding window that returns a 429, and a successful login clears the count. The frontend has proper sign in and register pages, keeps the token, attaches it automatically, guards the dashboard, restores the session on refresh, and handles sign out.

The statement pipeline handles CSV and PDF. Files are stored under random UUID names with an extension check and a size limit. CSV parsing normalizes different bank column names to a common set. PDF parsing uses pdfplumber, tries tables first and falls back to reading lines of text, and produces the exact same row shape the CSV parser does, so nothing downstream cares which format it came from. Locked PDFs are decrypted at upload with pikepdf, and the password is only ever used in memory and never stored. After parsing, the cleaning step deals with different date formats, currency symbols, thousands separators, and blank cells. Nothing is written until you confirm a preview, and a duplicate guard stops the same statement being imported twice.

Privacy. Before a transaction is stored, its description runs through a redaction step that removes account numbers, CIF, IFSC and PAN. The regexes are ordered so the specific patterns run before the general catch-all. This happens for both CSV and PDF imports, and the dashboard tells the user it is being done.

Categorization is rule based, with a confidence score and the keyword that matched, applied automatically when transactions are imported.

Analytics covers a fair amount. A summary with income, expenses, savings rate, category breakdown and biggest expense. A per month breakdown and a month over month comparison with short plain notes on what changed. Recurring payment detection based on how regular the intervals are and how steady the amounts are. And anomaly detection with two methods the user can switch between, z-score and IQR, each giving a readable reason.

The dashboard and design. The look is the Modern Ledger system, drawn from bookkeeping. A marble brand panel with gold veining, black and red for money in and out, and monospaced tabular figures. The dashboard shows the whole analytics engine, summary, categories, monthly trend, comparison, subscriptions and anomalies, with color spread through graduated bars, tinted cards and small accents. It is responsive.

## Project structure

Backend:

```
backend/
  requirements.txt
  .env                    (git-ignored)
  finsight.db             (git-ignored)
  uploads/                (git-ignored)
  app/
    main.py
    core/                 config, security, rate_limit
    db/
    models/               User, Statement, Transaction, Subscription
    schemas/
    services/             csv_parser, pdf_parser, cleaner, redact,
                          categorizer, analytics, subscriptions, anomalies
    api/
      deps.py
      routers/            auth, users, statements, analytics
```

Frontend:

```
frontend/
  src/
    main.jsx
    App.jsx
    index.css
    context/AuthContext.jsx
    lib/                  api.js, auth.js, format.js
    components/           Button, TextField, AuthLayout, ProtectedRoute
    pages/                Login, Register, Upload, Dashboard
```

## Data models

User has an id, a unique email, a full name, the hashed password, an active flag and a created date. Statement has an id, its owner, the original filename, the stored UUID filename, the file type, a status and an upload time. Transaction has an id, its owner, the statement it came from, a date, a redacted description, an amount, a type of income or expense, a category, a balance and a created time. Subscription has an id, its owner, the merchant, the average amount, the frequency, how many times it occurred, an estimated annual cost, a confidence, the last payment, a dismissed flag and a detected time.

## API endpoints

Auth:
- POST /api/auth/register
- POST /api/auth/login, rate limited
- GET /api/users/me, protected

Statements:
- POST /api/statements/upload, validates, stores, and decrypts PDFs with an optional password
- GET /api/statements
- GET /api/statements/{id}/preview
- POST /api/statements/{id}/confirm, redacts, categorizes, de-duplicates and stores
- GET /api/statements/{id}/transactions
- POST /api/statements/{id}/categorize

Analytics:
- GET /api/analytics/summary
- GET /api/analytics/monthly
- GET /api/analytics/comparison
- GET /api/analytics/subscriptions, POST .../detect, GET .../saved, PATCH .../{id}/dismiss
- GET /api/analytics/anomalies?method=zscore or iqr

## Decisions and problems worth noting

The PDF parser reuses the CSV parser's column vocabulary and returns the same rows, so cleaning, redaction, categorization and de-duplication don't care about the source format. That one decision is what kept the PDF feature small.

Redaction runs before categorization and before the database write, so sensitive data never lands in a stored row. I checked this on both CSV and PDF imports.

Encrypted PDFs are decrypted once, in memory, when they are uploaded. A missing or wrong password fails cleanly before any record gets created, so there is no orphaned file or half import.

Empty cells turn into NaN in pandas, which isn't valid JSON, and pandas can quietly turn None back into NaN inside a float column, so values only get cleaned to None after they leave the DataFrame.

Day first date parsing was corrupting ISO dates, so ISO format is detected first and day first is only applied to the rest.

Subscription detection needed a floor. It requires a few occurrences and a check on how consistent the amounts are before it calls something recurring, otherwise coincidences get flagged.

The two anomaly methods exist on purpose. A single large outlier drags up the mean and standard deviation that z-score depends on, which can hide smaller anomalies, while the median based IQR method isn't thrown off the same way. Having both with a live toggle makes that trade off something you can show rather than just describe.

The duplicate guard keys on owner, date, description and amount, so re-importing the same statement adds nothing. Its limit is that a duplicate with a reworded description would slip past the exact match.

## Security

Passwords are hashed, data is separated per user, identifiers are redacted before storage, PDF passwords stay in memory, and logins are rate limited. SECURITY.md has the full account, including the parts I would still harden before this went to production.

## Running it locally

Both servers run together.

Backend:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
fastapi dev app/main.py
```

Add a .env with a SECRET_KEY and token settings first. It serves on http://localhost:8000.

Frontend:

```
cd frontend
npm install
npm run dev
```

It serves on http://localhost:5173.

## Roadmap

An LLM based extraction path for PDF layouts the current parser can't handle. XLSX support. A financial health score with budget and savings goal suggestions. Cash flow prediction and written summaries. Data export. And an automated test suite.
