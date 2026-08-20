import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.services.csv_parser import parse_csv
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

router = APIRouter(prefix="/api/statements", tags=["statements"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf"}


@router.post("/upload", response_model=StatementRead, status_code=201)
async def upload_statement(
    file: UploadFile = File(...),
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
    # Fetch the statement, scoped to this user (isolation).
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == current_user.id)
        .first()
    )
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    if statement.file_type != "csv":
        raise HTTPException(
            status_code=400,
            detail="Preview currently supports CSV only. XLSX and PDF are coming.",
        )

    file_path = os.path.join(settings.UPLOAD_DIR, statement.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file is missing.")

    try:
        raw_rows = parse_csv(file_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

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

    if statement.file_type != "csv":
        raise HTTPException(status_code=400, detail="Only CSV import is supported so far.")

    file_path = os.path.join(settings.UPLOAD_DIR, statement.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file is missing.")

    try:
        raw_rows = parse_csv(file_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    cleaned = clean_transactions(raw_rows)
    if not cleaned:
        raise HTTPException(status_code=422, detail="No valid transactions found to import.")

    # Build Transaction rows and save them all in one commit.
    new_transactions = []
    for row in cleaned:
        # Categorize at import time, using the same service the manual endpoint uses.
        guess = categorize(row["description"], row["transaction_type"])
        txn = Transaction(
            user_id=current_user.id,
            statement_id=statement.id,
            date=date_type.fromisoformat(row["date"]),
            description=row["description"],
            amount=row["amount"],
            transaction_type=row["transaction_type"],
            balance=row["balance"],
            category=guess["category"],   # <-- set on creation, not left as default
        )
        db.add(txn)
        new_transactions.append(txn)

    statement.status = "processed"
    db.commit()

    for txn in new_transactions:
        db.refresh(txn)
    return new_transactions


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
        txn.category = guess["category"]   # persist the category on the stored row
        results.append({
            "id": txn.id,
            "description": txn.description,
            "category": guess["category"],
            "confidence": guess["confidence"],
            "matched_keyword": guess["matched_keyword"],
        })

    db.commit()   # save all the updated categories at once

    return {
        "statement_id": statement.id,
        "categorized_count": len(results),
        "results": results,
    }