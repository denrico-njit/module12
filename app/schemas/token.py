# app/schemas/token.py

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
