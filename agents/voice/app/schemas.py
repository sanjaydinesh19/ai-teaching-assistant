from pydantic import BaseModel, Field
from typing import Literal

class VoiceAskRequest(BaseModel):
    audio_file_id: str
    level: str = Field(..., description="e.g., 'grade-5'")
    visual_format: Literal["board-notes","steps","story"] = "board-notes"
    max_seconds: int = Field(90, ge=15, le=180)

class VoiceAskResponse(BaseModel):
    transcript: str
    explanation: str
    audio_url: str
