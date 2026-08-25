from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.deps import get_current_user
from app.services.analytics import summarize
from app.services.analytics import summarize, summarize_by_month
from app.services.analytics import summarize, summarize_by_month, compare_last_two_months
from app.services.subscriptions import detect_subscriptions
from datetime import date as date_type
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionRead
from app.services.anomalies import detect_anomalies

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
    
@router.post("/subscriptions/detect", response_model=list[SubscriptionRead])
def detect_and_store_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    found = detect_subscriptions(transactions)

    # Re-detection strategy: remove old auto-detected rows, but KEEP the user's
    # dismissals so a false positive they rejected doesn't reappear.
    dismissed_merchants = {
        s.merchant for s in db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.user_dismissed == True,
        ).all()
    }
    db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.user_dismissed == False,
    ).delete()

    stored = []
    for sub in found:
        if sub["merchant"] in dismissed_merchants:
            continue  # respect the user's earlier "not a subscription" call
        row = Subscription(
            user_id=current_user.id,
            merchant=sub["merchant"],
            average_amount=sub["average_amount"],
            frequency=sub["frequency"],
            occurrences=sub["occurrences"],
            estimated_annual_cost=sub["estimated_annual_cost"],
            confidence=sub["confidence"],
            last_payment=date_type.fromisoformat(sub["last_payment"]),
        )
        db.add(row)
        stored.append(row)

    db.commit()
    for row in stored:
        db.refresh(row)
    return stored


@router.get("/subscriptions/saved", response_model=list[SubscriptionRead])
def list_saved_subscriptions(
    include_dismissed: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Subscription).filter(Subscription.user_id == current_user.id)
    if not include_dismissed:
        query = query.filter(Subscription.user_dismissed == False)
    return query.order_by(Subscription.confidence.desc()).all()


@router.patch("/subscriptions/{subscription_id}/dismiss", response_model=SubscriptionRead)
def dismiss_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id)
        .first()
    )
    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.user_dismissed = True
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/anomalies")
def anomalies(
    method: str = "zscore",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    return detect_anomalies(transactions, method=method)