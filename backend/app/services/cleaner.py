import math
import re
import pandas as pd

# Matches currency symbols, commas, and whitespace to strip from amounts.
_CURRENCY_CHARS = re.compile(r"[₹$,\s]")


def _to_float(value):
    """Convert a messy amount (string or number) into a float, or None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return float(value)
    # It's a string like "1,299" or "₹ 241" — strip the noise, then convert.
    cleaned = _CURRENCY_CHARS.sub("", str(value))
    if cleaned in ("", "-"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(value):
    """Parse many date formats into an ISO 'YYYY-MM-DD' string, or None.

    ISO input (YYYY-MM-DD) is unambiguous, so we parse it WITHOUT dayfirst —
    forcing dayfirst on ISO wrongly swaps the month and day. Only non-ISO
    formats (like Indian DD/MM/YYYY statements) get the dayfirst hint.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    is_iso = bool(re.match(r"^\d{4}-\d{2}-\d{2}", text))
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=(not is_iso))
    if pd.isnull(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def clean_transactions(rows: list[dict]) -> list[dict]:
    """Normalize raw parsed rows into transactions with a single signed
    meaning: amount (magnitude) + transaction_type + a real date."""
    cleaned = []
    for row in rows:
        date = _parse_date(row.get("date"))
        description = (str(row.get("description") or "").strip()) or "Unknown"

        debit = _to_float(row.get("debit"))
        credit = _to_float(row.get("credit"))
        amount_field = _to_float(row.get("amount"))
        balance = _to_float(row.get("balance"))

        amount = None
        txn_type = "unknown"

        if debit and debit > 0:
            amount = debit
            txn_type = "expense"
        elif credit and credit > 0:
            amount = credit
            txn_type = "income"
        elif amount_field is not None:
            # Single-column format: negative = money out, positive = money in.
            amount = abs(amount_field)
            txn_type = "expense" if amount_field < 0 else "income"

        # A transaction we can't read (no amount or no date) is skipped, not guessed.
        if amount is None or date is None:
            continue

        cleaned.append({
            "date": date,
            "description": description,
            "amount": round(amount, 2),
            "transaction_type": txn_type,
            "balance": balance,
        })
    return cleaned