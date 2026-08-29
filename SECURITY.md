# Security

This document describes FinSight AI's security posture: the protections that are
implemented, and — just as importantly — the known limitations and what would be
hardened for a production deployment. It is written to be honest about the
boundary between "safe for a real project" and "production-grade."

## Implemented protections

**Password storage.** Passwords are hashed with **bcrypt** (per-password salt) and
never stored or logged in plaintext. Login verifies by hashing the submitted
password and comparing — the original is never recoverable from the database.

**Authentication.** Access is controlled with **JWTs** signed using a secret key
(HS256) and carrying an expiry (`exp`). Tokens are verified by signature and
expiry on every protected request. The scheme is **stateless** — no server-side
session store — which keeps it simple and scalable.

**Per-user data isolation.** Every database query for statements, transactions,
subscriptions, and analytics is filtered by the authenticated user's id. One user
cannot read or affect another user's data, even by guessing record ids.

**Upload safety.** Uploaded files are stored under **randomly generated UUID
filenames**, never the user-supplied name — this prevents path-traversal and
filename-collision attacks. Uploads are validated against an **extension
allowlist** (CSV, PDF) and a **size limit**.

**Cross-origin policy.** CORS is restricted to explicit development origins
(`localhost:5173`, `127.0.0.1:5173`), not a permissive wildcard, so only the
intended frontend can call the API from a browser.

**Privacy — identifier redaction.** Before any transaction is written to the
database, its description is passed through a redaction step that strips account
numbers, CIF numbers, IFSC codes, PAN, and long digit runs, replacing them with
safe placeholders (e.g. `[ACCOUNT]`, `[IFSC]`). Sensitive identifiers therefore
never reach stored transaction data. *(Best-effort, regex-based — see limitations.)*

**PDF password handling.** Passwords for encrypted PDF statements are used **only
in memory**, once, to decrypt at upload time. They are never stored, logged, or
returned in any response.

**Login rate limiting.** Repeated failed logins from the same client are throttled
(5 failures per 5-minute sliding window → HTTP 429), which blunts brute-force
password guessing. Successful logins reset the counter, so legitimate use is
unaffected.

## Known limitations and production hardening

These are conscious trade-offs appropriate for a development/academic build, with
the production-grade alternative noted for each.

**Token storage (XSS exposure).** The JWT is stored in the browser's
`localStorage`, which is readable by JavaScript and therefore exposed if the app
ever has a cross-site-scripting (XSS) flaw. *Production:* store the token in an
**httpOnly cookie** (unreadable by JS) with **CSRF protection**.

**Transport (no TLS in dev).** Development runs over plain HTTP, so tokens and
passwords travel unencrypted on the local machine. *Production:* serve over
**HTTPS/TLS** so credentials cannot be sniffed in transit.

**Rate limiter scope.** The limiter is **in-memory and per-process**, so it resets
on restart and is not shared across multiple server workers. It is keyed on client
IP, which behind a proxy would see the proxy's address. *Production:* a
**Redis-backed** limiter (e.g. `slowapi`) shared across workers, keyed on IP and/or
username, honouring `X-Forwarded-For` from a trusted proxy.

**Secret management.** The JWT `SECRET_KEY` is loaded from a git-ignored `.env`
file. If it were ever committed, tokens could be forged. *Production:* inject the
secret from a **secrets manager / environment**, and rotate it.

**Database.** SQLite is used for development — file-based and zero-config, but weak
under high write concurrency. *Production:* **PostgreSQL** (a connection-string
change, since data access goes through the SQLAlchemy ORM).

**Raw uploaded files retain sensitive data.** Redaction protects the *database*,
but the original uploaded statement (CSV/PDF, decrypted) still sits on disk with
full account numbers. *Production:* **encrypt at rest** and/or **delete the raw
file** once transactions are extracted.

**File validation is extension-based.** Uploads are checked by extension and size,
not by verifying the file's actual content is a safe, well-formed statement.
*Production:* validate content/MIME and scan untrusted uploads.

**Password policy.** Only a minimum length (8 characters) is enforced.
*Production:* add complexity/breach-list checks and optional MFA.

**Redaction is best-effort.** The regex approach masks labelled identifiers and
long digit runs, but an unlabelled, short account number could slip through, and
it is not a guarantee. It reduces exposure; it does not eliminate it.

**Duplicate-guard integrity note (not a vulnerability).** Re-importing a statement
is safe from double-counting because a content-based guard skips transactions
matching an existing `date + description + amount`. Its limit is that a duplicate
whose description was *reworded* would not be caught; a more robust version would
fuzzy-match descriptions or use a bank-provided transaction reference id.

## Reporting

This is an academic capstone project. Security concerns can be raised via the
repository's issue tracker.
