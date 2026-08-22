from collections import defaultdict


def summarize(transactions: list) -> dict:
    """Compute a financial summary from a list of Transaction rows.
    Only income/expense types count toward totals; anything else is ignored.
    """
    total_income = 0.0
    total_expenses = 0.0
    spending_by_category = defaultdict(float)
    biggest_expense = None

    for txn in transactions:
        amount = txn.amount or 0.0
        if txn.transaction_type == "income":
            total_income += amount
        elif txn.transaction_type == "expense":
            total_expenses += amount
            spending_by_category[txn.category] += amount
            if biggest_expense is None or amount > biggest_expense["amount"]:
                biggest_expense = {
                    "amount": round(amount, 2),
                    "description": txn.description,
                    "date": txn.date.isoformat() if txn.date else None,
                }

    net_savings = total_income - total_expenses
    # Guard against divide-by-zero when there's no income yet.
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    # Category breakdown, sorted biggest-spend first.
    category_breakdown = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in sorted(
            spending_by_category.items(), key=lambda item: item[1], reverse=True
        )
    ]

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": round(savings_rate, 1),
        "transaction_count": len(transactions),
        "top_category": category_breakdown[0]["category"] if category_breakdown else None,
        "biggest_expense": biggest_expense,
        "spending_by_category": category_breakdown,
    }
    
def summarize_by_month(transactions: list) -> list:
    """Group transactions by year-month and summarize each month.
    Returns a list sorted oldest-to-newest, one entry per month present.
    """
    months = defaultdict(lambda: {
        "income": 0.0,
        "expenses": 0.0,
        "by_category": defaultdict(float),
    })

    for txn in transactions:
        if txn.date is None:
            continue
        # Derive the bucket key: a date(2026, 8, 1) -> "2026-08".
        month_key = txn.date.strftime("%Y-%m")
        amount = txn.amount or 0.0

        if txn.transaction_type == "income":
            months[month_key]["income"] += amount
        elif txn.transaction_type == "expense":
            months[month_key]["expenses"] += amount
            months[month_key]["by_category"][txn.category] += amount

    # Turn the grouped data into a clean, sorted list.
    result = []
    for month_key in sorted(months.keys()):
        data = months[month_key]
        income = data["income"]
        expenses = data["expenses"]
        net = income - expenses
        result.append({
            "month": month_key,
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_savings": round(net, 2),
            "savings_rate": round((net / income * 100) if income > 0 else 0.0, 1),
            "spending_by_category": {
                cat: round(total, 2) for cat, total in data["by_category"].items()
            },
        })
    return result

def _percent_change(current: float, previous: float):
    """Percentage change from previous to current.
    Returns None when there's no meaningful percentage (new or gone)."""
    if previous == 0:
        return None  # can't compute % from a zero base; caller labels it 'new'
    return round((current - previous) / previous * 100, 1)


def _change_entry(current: float, previous: float) -> dict:
    """Build a single comparison record: values, absolute diff, % change, direction."""
    diff = round(current - previous, 2)
    pct = _percent_change(current, previous)

    if previous == 0 and current > 0:
        direction = "new"
    elif current == 0 and previous > 0:
        direction = "gone"
    elif diff > 0:
        direction = "up"
    elif diff < 0:
        direction = "down"
    else:
        direction = "same"

    return {
        "current": round(current, 2),
        "previous": round(previous, 2),
        "difference": diff,
        "percent_change": pct,
        "direction": direction,
    }


def compare_last_two_months(transactions: list) -> dict:
    """Compare the two most recent months present in the data.
    Returns per-field and per-category changes, plus a 'what_changed' list
    of the most notable movements.
    """
    monthly = summarize_by_month(transactions)

    if len(monthly) < 2:
        return {
            "comparable": False,
            "reason": "Need at least two months of data to compare.",
            "months_available": len(monthly),
        }

    previous = monthly[-2]   # summarize_by_month is sorted oldest->newest
    current = monthly[-1]

    # Top-level comparisons.
    income = _change_entry(current["income"], previous["income"])
    expenses = _change_entry(current["expenses"], previous["expenses"])
    savings = _change_entry(current["net_savings"], previous["net_savings"])

    # Per-category: union of categories from both months.
    cur_cats = current["spending_by_category"]
    prev_cats = previous["spending_by_category"]
    all_categories = set(cur_cats) | set(prev_cats)

    category_changes = {}
    for cat in all_categories:
        category_changes[cat] = _change_entry(
            cur_cats.get(cat, 0.0),
            prev_cats.get(cat, 0.0),
        )

    # "What Changed?" — surface the notable movements as readable sentences.
    what_changed = []
    if expenses["direction"] == "up":
        what_changed.append(
            f"Total spending increased by ₹{expenses['difference']:.0f}"
            + (f" ({expenses['percent_change']}%)" if expenses["percent_change"] is not None else "")
            + " compared with last month."
        )
    elif expenses["direction"] == "down":
        what_changed.append(
            f"Total spending decreased by ₹{abs(expenses['difference']):.0f}"
            + (f" ({abs(expenses['percent_change'])}%)" if expenses["percent_change"] is not None else "")
            + " compared with last month."
        )

    for cat, change in category_changes.items():
        if change["direction"] == "new":
            what_changed.append(f"New spending in {cat}: ₹{change['current']:.0f} this month.")
        elif change["direction"] == "up" and change["percent_change"] is not None and change["percent_change"] >= 30:
            what_changed.append(
                f"{cat} spending increased {change['percent_change']}% "
                f"(₹{change['previous']:.0f} → ₹{change['current']:.0f})."
            )
        elif change["direction"] == "down" and change["percent_change"] is not None and change["percent_change"] <= -30:
            what_changed.append(
                f"{cat} spending decreased {abs(change['percent_change'])}% "
                f"(₹{change['previous']:.0f} → ₹{change['current']:.0f})."
            )

    return {
        "comparable": True,
        "current_month": current["month"],
        "previous_month": previous["month"],
        "income": income,
        "expenses": expenses,
        "net_savings": savings,
        "category_changes": category_changes,
        "what_changed": what_changed,
    }