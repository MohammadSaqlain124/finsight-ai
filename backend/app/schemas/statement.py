from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StatementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    original_filename: str
    file_type: str
    status: str
    uploaded_at: datetime