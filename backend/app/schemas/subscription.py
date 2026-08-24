from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    merchant: str
    average_amount: float
    frequency: str
    occurrences: int
    estimated_annual_cost: float
    confidence: float
    last_payment: date | None
    user_dismissed: bool
    detected_at: datetime