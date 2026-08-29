# Security

This is an honest account of where FinSight AI stands on security. What is actually protected, and what I would still need to harden before calling it production ready. I've tried not to overstate anything.

## What's protected

Passwords are hashed with bcrypt, each with its own salt, and never stored or logged in plain text. Login checks a password by hashing it and comparing, so the original can't be recovered from the database.

Access is controlled with JWTs, signed with a secret key and carrying an expiry. Every protected request checks the signature and the expiry. There is no server side session store, which keeps the setup simple and easy to scale.

Every query for statements, transactions, subscriptions and analytics is filtered by the logged in user's id, so one user can't reach another's data even by guessing record ids.

Uploaded files are saved under random UUID filenames rather than whatever the user's file was called, which avoids path traversal and filename collisions. Uploads are checked against an allowed list of extensions and a size limit.

CORS only allows the frontend's own origin during development, not a wildcard, so a random site can't call the API from someone's browser.

On privacy, every transaction description is run through a redaction step before it is stored. Account numbers, CIF, IFSC and PAN are replaced with placeholders, and the specific patterns are checked before the general catch-all. Sensitive identifiers don't reach stored data. It is regex based and best effort, which I come back to below.

Passwords for encrypted PDFs are only used in memory, once, to decrypt the file at upload. They are never stored, logged, or returned in a response.

Logins are rate limited. Too many failed attempts from one client in a short window get blocked with a 429, which takes the sting out of brute forcing. A successful login resets the count, so normal use isn't affected.

## What I'd harden for production

These are deliberate trade offs for a development and academic build, with what I would do differently noted for each.

The token is kept in the browser's localStorage, which JavaScript can read, so a cross site scripting bug would expose it. The stronger option is an httpOnly cookie that JavaScript can't touch, with CSRF protection added.

Development runs over plain HTTP, so nothing is encrypted on the wire locally. Production would run over HTTPS so tokens and passwords can't be sniffed in transit.

The rate limiter lives in memory in a single process, so it resets on restart and isn't shared across multiple workers. It is keyed on client IP, which behind a proxy would only see the proxy. A production version would use something like a Redis backed limiter shared across workers, keyed on IP and username, reading the real client IP from a trusted proxy header.

The JWT secret key is loaded from a git-ignored .env file. If it ever got committed, tokens could be forged. In production the secret should come from a secrets manager and be rotated.

SQLite is fine for development but doesn't hold up well under heavy concurrent writes. Because data access goes through the SQLAlchemy ORM, moving to PostgreSQL is mostly a connection string change.

Redaction protects the database, but the original uploaded file still sits on disk with full account numbers in it. Production would encrypt those at rest, or delete the raw file once the transactions have been pulled out.

File validation only checks the extension and size, not that the contents are actually a safe, well formed statement. A production version would check the real content and scan untrusted uploads.

The password policy only enforces a minimum length of eight characters. Adding complexity or breach list checks, and optional MFA, would be the next step.

Redaction is best effort. It catches labelled identifiers and long runs of digits, but a short, unlabelled account number could get through. It reduces exposure, it doesn't guarantee it.

One last thing that isn't a vulnerability but is worth being clear about. Re-importing a statement won't double count, because a transaction matching an existing one on date, description and amount is skipped. The limit is that a duplicate whose description was reworded wouldn't be caught. A stronger version would fuzzy match descriptions or use a bank's own transaction reference.

## Reporting

This is an academic project. Anything security related can be raised through the repository's issue tracker.
