from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    description: str
    amount: float
    transaction_type: str
    category: str
    balance: float | None
    created_at: datetime