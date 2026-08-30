import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.services.csv_parser import parse_csv
from app.services.pdf_parser import parse_pdf, decrypt_pdf_in_place, PDFPasswordError
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.models.statement import Statement
from app.schemas.statement import StatementRead
from app.api.deps import get_current_user
from app.services.cleaner import clean_transactions
from datetime import date as date_type
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionRead
from app.services.categorizer import categorize
from app.services.redact import redact_text
from app.models.subscription import Subscription

router = APIRouter(prefix="/api/statements", tags=["statements"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf"}


def _parse_statement(statement) -> list[dict]:
    """Route a stored statement to the right parser based on its file type,
    returning raw rows in the shared internal shape."""
    file_path = os.path.join(settings.UPLOAD_DIR, statement.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file is missing.")

    try:
        if statement.file_type == "csv":
            return parse_csv(file_path)
        if statement.file_type == "pdf":
            return parse_pdf(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"{statement.file_type.upper()} import is not supported yet.",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PDFPasswordError as e:
        # PDFs are decrypted at upload, so this should be rare — guards the case
        # of a stored PDF somehow still encrypted.
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=StatementRead, status_code=201)
async def upload_statement(
    file: UploadFile = File(...),
    password: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Validate the extension
    original_name = file.filename or "upload"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: CSV, XLSX, PDF.",
        )

    # 2. Read the file and enforce a size limit
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum is {settings.MAX_UPLOAD_MB} MB.",
        )

    # 3. Save to disk under a RANDOM name — never trust the user's filename
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(contents)

    # 3b. If it's a PDF, decrypt it now (password used once, then discarded).
    #     On failure, remove the file and bail BEFORE creating a DB row, so no
    #     orphaned file or statement record is left behind.
    if ext == ".pdf":
        try:
            decrypt_pdf_in_place(stored_path, password)
        except PDFPasswordError as e:
            os.remove(stored_path)
            raise HTTPException(status_code=400, detail=str(e))

    # 4. Record it in the database, bound to THIS user
    statement = Statement(
        user_id=current_user.id,
        original_filename=original_name,
        stored_filename=stored_name,
        file_type=ext.lstrip("."),
        status="uploaded",
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement


@router.get("", response_model=list[StatementRead])
def list_my_statements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Statement)
        .filter(Statement.user_id == current_user.id)   # <-- isolation
        .order_by(Statement.uploaded_at.desc())
        .all()
    )


@router.get("/{statement_id}/preview")
def preview_statement(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == current_user.id)
        .first()
    )
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    raw_rows = _parse_statement(statement)
    transactions = clean_transactions(raw_rows)

    return {
        "statement_id": statement.id,
        "raw_row_count": len(raw_rows),
        "transaction_count": len(transactions),
        "preview": transactions[:20],
    }


@router.post("/{statement_id}/confirm", response_model=list[TransactionRead], status_code=201)
def confirm_import(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == current_user.id)
        .first()
    )
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    # Guard: don't import the same statement twice.
    if statement.status == "processed":
        raise HTTPException(status_code=400, detail="This statement has already been imported.")

    raw_rows = _parse_statement(statement)
    cleaned = clean_transactions(raw_rows)
    if not cleaned:
        raise HTTPException(status_code=422, detail="No valid transactions found to import.")

    new_transactions = []
    skipped_duplicates = 0
    for row in cleaned:
        txn_date = date_type.fromisoformat(row["date"])

        # Duplicate guard: skip identical transaction (same user + date + description + amount).
        existing = (
            db.query(Transaction)
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.date == txn_date,
                Transaction.description == row["description"],
                Transaction.amount == row["amount"],
            )
            .first()
        )
        if existing is not None:
            skipped_duplicates += 1
            continue

        # Privacy: strip account numbers, CIF, IFSC, PAN from the narration
        # BEFORE it is categorized or written to the database.
        row["description"] = redact_text(row["description"])

        guess = categorize(row["description"], row["transaction_type"])
        txn = Transaction(
            user_id=current_user.id,
            statement_id=statement.id,
            date=txn_date,
            description=row["description"],
            amount=row["amount"],
            transaction_type=row["transaction_type"],
            balance=row["balance"],
            category=guess["category"],
        )
        db.add(txn)
        new_transactions.append(txn)

    statement.status = "processed"
    db.commit()

    for txn in new_transactions:
        db.refresh(txn)
    return new_transactions

@router.delete("/reset")
def reset_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all of the current user's transactions, statements, and detected
    subscriptions, and remove their uploaded files from disk. The account itself
    is left intact. This is irreversible."""
    statements = (
        db.query(Statement).filter(Statement.user_id == current_user.id).all()
    )

    # Counts for the response summary.
    txn_count = db.query(Transaction).filter(Transaction.user_id == current_user.id).count()
    sub_count = db.query(Subscription).filter(Subscription.user_id == current_user.id).count()
    stmt_count = len(statements)

    # Remove the raw uploaded files, which still contain full statement data.
    for s in statements:
        path = os.path.join(settings.UPLOAD_DIR, s.stored_filename)
        if os.path.exists(path):
            os.remove(path)

    # Delete rows for THIS user only, in a foreign-key-safe order:
    # transactions reference statements, so they go first.
    db.query(Transaction).filter(Transaction.user_id == current_user.id).delete(synchronize_session=False)
    db.query(Subscription).filter(Subscription.user_id == current_user.id).delete(synchronize_session=False)
    db.query(Statement).filter(Statement.user_id == current_user.id).delete(synchronize_session=False)
    db.commit()

    return {
        "deleted": {
            "transactions": txn_count,
            "statements": stmt_count,
            "subscriptions": sub_count,
        }
    }


@router.get("/{statement_id}/transactions", response_model=list[TransactionRead])
def list_statement_transactions(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == current_user.id)
        .first()
    )
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    return (
        db.query(Transaction)
        .filter(Transaction.statement_id == statement.id)
        .order_by(Transaction.date)
        .all()
    )


@router.post("/{statement_id}/categorize")
def categorize_statement(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == current_user.id)
        .first()
    )
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.statement_id == statement.id)
        .all()
    )
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found. Import them first.")

    results = []
    for txn in transactions:
        guess = categorize(txn.description, txn.transaction_type)
        txn.category = guess["category"]
        results.append({
            "id": txn.id,
            "description": txn.description,
            "category": guess["category"],
            "confidence": guess["confidence"],
            "matched_keyword": guess["matched_keyword"],
        })

    db.commit()

    return {
        "statement_id": statement.id,
        "categorized_count": len(results),
        "results": results,
    }