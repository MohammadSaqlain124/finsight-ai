from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.deps import get_current_user
from app.services.analytics import summarize

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)   # only THIS user's data
        .all()
    )
    return summarize(transactions)