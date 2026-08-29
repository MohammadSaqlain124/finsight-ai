import io
import re
import pdfplumber
import pikepdf

# Reuse the same column vocabulary as the CSV parser so PDF tables normalize
# to the exact same internal keys — cleaner / redact / categorize stay unchanged.
COLUMN_ALIASES = {
    "date": ["date", "txn date", "transaction date", "value date", "posting date"],
    "description": ["description", "narration", "particulars", "details", "remarks", "transaction details"],
    "debit": ["debit", "withdrawal", "withdrawal amt", "dr", "debit amount"],
    "credit": ["credit", "deposit", "deposit amt", "cr", "credit amount"],
    "amount": ["amount", "amt", "transaction amount"],
    "balance": ["balance", "closing balance", "running balance", "available balance"],
}


class PDFPasswordError(Exception):
    """PDF is encrypted and the password is missing or wrong."""


def _map_header(header_cells):
    """Map a table's header cells to our internal column names.
    Returns {column_index: internal_name}."""
    mapping = {}
    for i, cell in enumerate(header_cells):
        if not cell:
            continue
        norm = str(cell).strip().lower()
        for internal, aliases in COLUMN_ALIASES.items():
            if norm in aliases:
                mapping[i] = internal
                break
    return mapping


def _decrypt_if_needed(file_path, password):
    """Return usable PDF bytes. If the file is encrypted, decrypt it with the
    password; raise PDFPasswordError if a password is needed but absent/wrong.
    The password is used only in memory and never stored."""
    with open(file_path, "rb") as f:
        raw = f.read()
    try:
        with pikepdf.open(io.BytesIO(raw)):
            return raw                      # opened without a password -> not encrypted
    except pikepdf.PasswordError:
        pass
    if not password:
        raise PDFPasswordError("This PDF is password-protected. Please provide the password.")
    try:
        out = io.BytesIO()
        with pikepdf.open(io.BytesIO(raw), password=password) as pdf:
            pdf.save(out)
        return out.getvalue()
    except pikepdf.PasswordError:
        raise PDFPasswordError("Incorrect password for this PDF.")


_LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}[-/][A-Za-z0-9]{2,9}[-/]\d{2,4})\s+"
    r"(?P<desc>.+?)\s+"
    r"(?P<amount>-?[\u20b9$]?\s?[\d,]+\.\d{2})\s*$"
)


def _parse_text_lines(pdf):
    """Fallback for statements without real table structure: match lines that
    start with a date and end with an amount."""
    rows = []
    for page in pdf.pages:
        for line in (page.extract_text() or "").splitlines():
            m = _LINE_RE.match(line.strip())
            if m:
                rows.append({
                    "date": m.group("date"),
                    "description": m.group("desc").strip(),
                    "amount": m.group("amount"),
                })
    return rows


def parse_pdf(file_path, password=None):
    """Extract transaction rows from a PDF statement, returning the same
    raw-row shape as parse_csv so clean_transactions works unchanged."""
    pdf_bytes = _decrypt_if_needed(file_path, password)
    rows = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                mapping = _map_header(table[0])
                if "date" not in mapping.values():
                    continue                      # not a transaction table
                for cells in table[1:]:
                    row = {}
                    for i, internal in mapping.items():
                        if i < len(cells):
                            val = cells[i]
                            row[internal] = str(val).strip() if val not in (None, "") else None
                    if any(row.values()):
                        rows.append(row)
        if not rows:
            rows = _parse_text_lines(pdf)

    if not rows:
        raise ValueError("Could not find any transaction rows in this PDF.")
    return rows