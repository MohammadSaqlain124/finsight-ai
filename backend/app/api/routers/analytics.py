from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.deps import get_current_user
from app.services.analytics import summarize
from app.services.analytics import summarize, summarize_by_month
from app.services.analytics import summarize, summarize_by_month, compare_last_two_months
from app.services.subscriptions import detect_subscriptions

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

@router.get("/monthly")
def monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    return {"months": summarize_by_month(transactions)}

@router.get("/comparison")
def monthly_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    return compare_last_two_months(transactions)

@router.get("/subscriptions")
def subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    found = detect_subscriptions(transactions)
    total_monthly = round(sum(
        s["average_amount"] for s in found if s["frequency"] == "monthly"
    ), 2)
    return {
        "count": len(found),
        "estimated_monthly_total": total_monthly,
        "subscriptions": found,
    }