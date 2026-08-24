import re
from collections import defaultdict
from statistics import mean, pstdev


def _normalize_merchant(description: str) -> str:
    """Reduce a description to a merchant key so 'NETFLIX SUBSCRIPTION' and
    'NETFLIX' group together. Lowercase, strip generic noise words, keep the
    first meaningful token(s)."""
    text = (description or "").lower()
    # Remove common noise words that vary between transactions.
    noise = ["subscription", "payment", "recharge", "order", "purchase",
             "autopay", "auto pay", "bill", "monthly", "annual"]
    for word in noise:
        text = text.replace(word, "")
    text = re.sub(r"[^a-z0-9 ]", " ", text)   # drop punctuation
    text = re.sub(r"\s+", " ", text).strip()
    # Use the first word as the merchant key (e.g. "netflix", "airtel").
    return text.split(" ")[0] if text else "unknown"


def detect_subscriptions(transactions: list) -> list:
    """Find likely recurring payments: same merchant, 2+ times, at a roughly
    regular interval. Returns one record per detected subscription."""
    # Group EXPENSE transactions by normalized merchant.
    by_merchant = defaultdict(list)
    for txn in transactions:
        if txn.transaction_type != "expense" or txn.date is None:
            continue
        key = _normalize_merchant(txn.description)
        by_merchant[key].append(txn)

    subscriptions = []
    for merchant, txns in by_merchant.items():
        if len(txns) < 2:
            continue  # can't establish a rhythm from a single payment

        txns.sort(key=lambda t: t.date)

        # Gaps (in days) between consecutive payments.
        gaps = [(txns[i].date - txns[i - 1].date).days for i in range(1, len(txns))]
        avg_gap = mean(gaps)
        gap_consistency = pstdev(gaps) if len(gaps) > 1 else 0

        # Classify the rhythm.
        if 25 <= avg_gap <= 35:
            frequency = "monthly"
        elif 6 <= avg_gap <= 8:
            frequency = "weekly"
        elif 13 <= avg_gap <= 16:
            frequency = "biweekly"
        elif 85 <= avg_gap <= 95:
            frequency = "quarterly"
        else:
            frequency = "irregular"

        amounts = [t.amount for t in txns]
        avg_amount = mean(amounts)

        # Confidence: higher when the interval is consistent AND it's a known rhythm.
        confidence = 0.5
        if frequency != "irregular":
            confidence += 0.3
        if gap_consistency <= 3:      # gaps barely vary -> strong rhythm
            confidence += 0.2
        confidence = round(min(confidence, 1.0), 2)

        # Estimated annual cost based on detected frequency.
        per_year = {"weekly": 52, "biweekly": 26, "monthly": 12,
                    "quarterly": 4, "irregular": len(txns)}
        estimated_annual = round(avg_amount * per_year[frequency], 2)

        subscriptions.append({
            "merchant": merchant,
            "sample_description": txns[-1].description,
            "occurrences": len(txns),
            "average_amount": round(avg_amount, 2),
            "frequency": frequency,
            "average_gap_days": round(avg_gap, 1),
            "last_payment": txns[-1].date.isoformat(),
            "estimated_annual_cost": estimated_annual,
            "confidence": confidence,
        })

    # Most confident, most expensive first.
    subscriptions.sort(key=lambda s: (s["confidence"], s["estimated_annual_cost"]), reverse=True)
    return subscriptions