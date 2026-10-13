
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    action: str = Field(..., min_length=2, max_length=100)
    entity_type: str = Field(..., min_length=2, max_length=100)
    entity_id: int | None = Field(default=None, gt=0)
    details: str | None = None
    ip_address: str | None = Field(default=None, max_length=45)


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    details: str | None
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
