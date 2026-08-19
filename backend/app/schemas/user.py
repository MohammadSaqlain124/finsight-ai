from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    """Shape of the data expected when someone registers."""
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    """Shape of the data we send back — notice NO password field."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime