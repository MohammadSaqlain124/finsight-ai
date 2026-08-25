from statistics import mean, pstdev, median


def _quartiles(sorted_vals: list[float]):
    """Return (Q1, Q3) using a simple, explainable method."""
    n = len(sorted_vals)
    mid = n // 2
    lower = sorted_vals[:mid]
    upper = sorted_vals[mid + 1:] if n % 2 else sorted_vals[mid:]
    return median(lower), median(upper)


def detect_anomalies(transactions: list, method: str = "zscore",
                     z_threshold: float = 2.5, iqr_factor: float = 1.5) -> dict:
    """Flag unusually LARGE expenses. Supports two methods:
      - 'zscore': flags amounts > mean + z_threshold * std
      - 'iqr':    flags amounts > Q3 + iqr_factor * IQR
    Never labels anything 'fraud' — only 'unusual', for the user to review.
    """
    expenses = [t for t in transactions if t.transaction_type == "expense"]

    # Need enough data before 'normal' is meaningful.
    if len(expenses) < 5:
        return {
            "method": method,
            "enough_data": False,
            "reason": "Need at least 5 expense transactions to detect anomalies.",
            "anomalies": [],
        }

    amounts = [t.amount for t in expenses]
    avg = mean(amounts)
    spread = pstdev(amounts)

    sorted_amounts = sorted(amounts)
    q1, q3 = _quartiles(sorted_amounts)
    iqr = q3 - q1

    # Compute the upper threshold once, based on chosen method.
    if method == "iqr":
        upper_threshold = q3 + iqr_factor * iqr
    else:  # default zscore
        upper_threshold = avg + z_threshold * spread

    anomalies = []
    for t in expenses:
        if t.amount <= upper_threshold:
            continue

        # Build an explainable reason (spec §30) for whichever method flagged it.
        if method == "iqr":
            reason = (
                f"₹{t.amount:.0f} is above the usual upper range of "
                f"₹{upper_threshold:.0f} (based on your typical spending spread)."
            )
            score = round((t.amount - q3) / iqr, 2) if iqr > 0 else None
        else:
            z = (t.amount - avg) / spread if spread > 0 else 0
            reason = (
                f"₹{t.amount:.0f} is {z:.1f}x standard deviations above your "
                f"average expense of ₹{avg:.0f}."
            )
            score = round(z, 2)

        anomalies.append({
            "id": t.id,
            "date": t.date.isoformat() if t.date else None,
            "description": t.description,
            "amount": round(t.amount, 2),
            "category": t.category,
            "score": score,
            "reason": reason,
        })

    anomalies.sort(key=lambda a: a["amount"], reverse=True)

    return {
        "method": method,
        "enough_data": True,
        "average_expense": round(avg, 2),
        "upper_threshold": round(upper_threshold, 2),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }