
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenInfo(BaseModel):
    id: int
    user_id: int
    expires_at: datetime
    is_revoked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
