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