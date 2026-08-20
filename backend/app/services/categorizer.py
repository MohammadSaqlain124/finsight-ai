# Each rule is (keyword, confidence). Keywords match case-insensitively as
# substrings of the transaction description. Specific merchant names carry
# high confidence; generic words carry lower confidence. This is the same
# alias-matching pattern you built for column headers in Phase 2.
CATEGORY_RULES = {
    "Food & Dining": [
        ("swiggy", 0.95), ("zomato", 0.95), ("dominos", 0.9), ("mcdonald", 0.9),
        ("kfc", 0.9), ("starbucks", 0.9), ("restaurant", 0.6), ("cafe", 0.6),
        ("food", 0.5),
    ],
    "Groceries": [
        ("bigbasket", 0.95), ("blinkit", 0.95), ("zepto", 0.95), ("dmart", 0.9),
        ("instamart", 0.9), ("reliance fresh", 0.9), ("grocery", 0.6),
    ],
    "Shopping": [
        ("amazon", 0.9), ("flipkart", 0.95), ("myntra", 0.95), ("ajio", 0.95),
        ("meesho", 0.9), ("lifestyle", 0.7), ("mall", 0.5),
    ],
    "Transportation": [
        ("uber", 0.95), ("ola", 0.9), ("rapido", 0.95), ("irctc", 0.9),
        ("fastag", 0.9), ("petrol", 0.8), ("fuel", 0.8), ("metro", 0.7),
    ],
    "Subscriptions": [
        ("netflix", 0.95), ("spotify", 0.95), ("hotstar", 0.9), ("prime video", 0.9),
        ("youtube premium", 0.9), ("jiosaavn", 0.9), ("subscription", 0.6),
    ],
    "Utilities/Bills": [
        ("airtel", 0.85), ("jio", 0.85), ("vodafone", 0.85), ("electricity", 0.9),
        ("broadband", 0.85), ("recharge", 0.7), ("gas bill", 0.85), ("bill", 0.4),
    ],
    "Healthcare": [
        ("apollo", 0.85), ("pharmeasy", 0.9), ("1mg", 0.9), ("netmeds", 0.9),
        ("pharmacy", 0.8), ("hospital", 0.8), ("clinic", 0.7),
    ],
    "Investments": [
        ("zerodha", 0.95), ("groww", 0.95), ("upstox", 0.9), ("mutual fund", 0.9),
        ("sip", 0.7),
    ],
    "Loan/EMI": [
        ("emi", 0.85), ("loan", 0.8), ("credit card payment", 0.8),
    ],
    "Income": [
        ("salary", 0.95), ("freelance", 0.85), ("interest", 0.8),
        ("cashback", 0.8), ("refund", 0.8), ("dividend", 0.8),
    ],
}


def categorize(description: str, transaction_type: str = "expense") -> dict:
    """Return the best category guess for a transaction description.

    Returns {category, confidence (0..1), matched_keyword}. Picks the single
    highest-confidence keyword match across all categories. Falls back to
    'Income' for income-type transactions with no keyword match, and
    'Uncategorized' (confidence 0) when nothing matches at all.
    """
    text = (description or "").lower()

    best_category = "Uncategorized"
    best_confidence = 0.0
    best_keyword = None

    for category, rules in CATEGORY_RULES.items():
        for keyword, confidence in rules:
            if keyword in text and confidence > best_confidence:
                best_category = category
                best_confidence = confidence
                best_keyword = keyword

    # Fallback: an income transaction we couldn't match by keyword is still Income.
    if best_category == "Uncategorized" and transaction_type == "income":
        return {"category": "Income", "confidence": 0.5, "matched_keyword": None}

    return {
        "category": best_category,
        "confidence": round(best_confidence, 2),
        "matched_keyword": best_keyword,
    }