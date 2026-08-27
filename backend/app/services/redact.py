import re

# Each pattern targets a specific class of sensitive identifier that can appear
# in a statement's transaction narration. Order matters: more specific patterns
# (IFSC, PAN) run before the generic long-digit-run catch-all, so they're
# labelled correctly rather than swallowed by the number rule.
_PATTERNS = [
    # IFSC code: 4 letters, a 0, then 6 alphanumerics (e.g. HDFC0001234)
    (re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"), "[IFSC]"),
    # PAN: 5 letters, 4 digits, 1 letter (e.g. ABCDE1234F)
    (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"), "[PAN]"),
    # CIF number: the label "CIF" followed by a run of digits
    (re.compile(r"\bCIF\s*:?\s*\d{6,}\b", re.IGNORECASE), "[CIF]"),
    # Account number: an explicit A/C label followed by digits
    (re.compile(r"\b(?:A/C|AC|ACCT|ACCOUNT)\s*:?\s*[Xx*]*\d{4,}\b", re.IGNORECASE), "[ACCOUNT]"),
    # Catch-all: any bare run of 9+ digits (long enough to be an account/card,
    # not a date, amount, or short reference). Runs LAST.
    (re.compile(r"\b\d{9,}\b"), "[REDACTED]"),
]


def redact_text(text: str) -> str:
    """Replace sensitive identifiers in a single string with safe placeholders.
    Returns the text unchanged if there's nothing sensitive in it."""
    if not text:
        return text
    result = text
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result