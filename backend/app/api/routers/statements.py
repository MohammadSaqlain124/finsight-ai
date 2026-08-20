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