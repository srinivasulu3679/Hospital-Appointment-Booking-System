
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationFileResponse(BaseModel):
    id: int
    consultation_id: int
    uploaded_by: int
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    file_size: int = Field(..., ge=0)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
