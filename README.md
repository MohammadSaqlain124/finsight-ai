# FinSight AI

**Live app:** https://finsight-ai-blond.vercel.app

FinSight AI is a personal finance analyzer I built for my final year B.Tech project. You upload a bank statement, either a CSV or a PDF, and it reads through the transactions, cleans them up, removes anything sensitive like account numbers, sorts them into categories, and shows you what your money is actually doing. Spending summaries, category breakdowns, monthly trends, recurring payments and a few other views, all on one dashboard.

I wrote it so I can explain every decision in it, not just get it running.

Author: Mohd Saqlain Hussain, B.Tech CSE, Invertis University

## What it does

You sign up and log in with an email and password. Passwords are hashed, and the login is rate limited so it can't be brute forced.

Once you're in, you upload a statement. Before anything is saved you get a preview of the parsed transactions so you can check the parsing looks right. Account numbers, CIF, IFSC and PAN are stripped out of the descriptions before they ever reach the database.

The dashboard then gives you net savings, income against expenses, savings rate, a category breakdown, your biggest expense, a monthly trend, a month over month comparison with short written notes on what changed, detected subscriptions, and unusual transactions. The anomaly view has a toggle between two methods, z-score and IQR. That's worth having because they don't always agree, and seeing the difference tells you something.

## Tech stack

The backend is FastAPI with SQLAlchemy over SQLite, written so a move to Postgres later wouldn't mean rewriting queries. Auth is JWT with bcrypt hashing. pandas handles the CSV work, and pdfplumber and pikepdf handle PDF extraction and decryption.

The frontend is React with Vite and react-router-dom. Styling is plain CSS with custom properties and CSS Modules rather than a UI framework, because I wanted full control over the look. Fonts are the IBM Plex family.

## Design

The interface has its own identity, which I called Modern Ledger. It borrows from the look of bookkeeping. There's a marble panel with gold veining on the login and a lighter version as the dashboard header, black for money coming in and a deep red for money going out, and monospaced figures so the numbers line up in columns like a real statement. It works on mobile too.

## Getting started

You run two servers at once.

Backend:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file in backend with a SECRET_KEY and your token settings, then run:

```
fastapi dev app/main.py
```

That serves on http://localhost:8000, with API docs at /docs.

Frontend:

```
cd frontend
npm install
npm run dev
```

That serves on http://localhost:5173. Open it, make an account, and upload a statement.

## Using it

Register, sign in, and click Upload on the dashboard. Pick a CSV or PDF, and if the PDF is locked, type its password. Check the preview, hit confirm, and the dashboard fills with your data.

A CSV needs columns it can recognise, so a date, a description, and either an amount column or separate debit and credit columns. PDFs work best when they are text based with a proper transaction table.

## Security

The short version is that passwords are hashed, each user only sees their own data, sensitive identifiers are redacted before storage, PDF passwords are only ever held in memory, and logins are rate limited. The full picture, including what I would still harden for production, is in SECURITY.md.

## Roadmap

A few things I would like to add. An LLM based extraction path for messy PDF layouts the current parser can't handle. XLSX support. A financial health score with budget and savings suggestions. Data export. And a proper test suite.
