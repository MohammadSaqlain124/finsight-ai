import pandas as pd
import math

# Maps many possible bank column names -> our single internal name.
# Keys are lowercased/stripped before matching, so "Txn Date" == "txn date".
COLUMN_ALIASES = {
    "date": ["date", "txn date", "transaction date", "value date", "posting date"],
    "description": ["description", "narration", "particulars", "details", "remarks", "transaction details"],
    "debit": ["debit", "withdrawal", "withdrawal amt", "dr", "debit amount"],
    "credit": ["credit", "deposit", "deposit amt", "cr", "credit amount"],
    "amount": ["amount", "amt", "transaction amount"],
    "balance": ["balance", "closing balance", "running balance", "available balance"],
}


def _build_reverse_map(columns: list[str]) -> dict[str, str]:
    """Given the actual columns in the file, figure out which one maps to
    each of our internal names. Returns {actual_column: internal_name}."""
    normalized = {col: col.strip().lower() for col in columns}
    reverse = {}
    for internal_name, aliases in COLUMN_ALIASES.items():
        for actual_col, norm in normalized.items():
            if norm in aliases:
                reverse[actual_col] = internal_name
                break
    return reverse


def parse_csv(file_path: str) -> list[dict]:
    """Read a CSV bank statement and return a list of normalized row dicts.
    Each dict has keys from our internal schema (whichever were found)."""
    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("The file contains no data rows.")

    # Rename the file's columns to our internal names.
    rename_map = _build_reverse_map(list(df.columns))
    if not rename_map:
        raise ValueError(
            "Could not recognize any expected columns "
            "(date, description, amount/debit/credit)."
        )
    df = df.rename(columns=rename_map)

    # Keep only the columns we understand.
    known_cols = [c for c in df.columns if c in COLUMN_ALIASES]
    df = df[known_cols]

    # Drop rows that are completely empty.
    df = df.dropna(how="all")

        # Convert the DataFrame into plain Python dicts, one per row.
    records = df.to_dict(orient="records")

    # Sanitize AFTER leaving the DataFrame: no dtype can coerce None back to
    # NaN here. Any leftover NaN/inf becomes None so the result is JSON-safe.
    clean_records = []
    for row in records:
        clean_row = {}
        for key, value in row.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                clean_row[key] = None
            else:
                clean_row[key] = value
        clean_records.append(clean_row)

    return clean_records