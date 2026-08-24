from datetime import datetime, timezone, date as date_type
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    merchant: Mapped[str] = mapped_column(String(100), nullable=False)
    average_amount: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_annual_cost: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    last_payment: Mapped[date_type] = mapped_column(Date, nullable=True)

    # Lets the user override a false positive without deleting the detection.
    user_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )