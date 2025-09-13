from pydantic import BaseModel, Field
from typing import Optional

class VoiceRequest(BaseModel):
    file_id: str = Field(..., description="Upload/file handle for WAV/MP3")
    target_language: str = Field(default="en")
    tts_voice: str = Field(default="alloy")  # your preferred voice
    tts_speed: float = Field(default=1.0, ge=0.5, le=1.5)  # playback speed
    topic_hint: Optional[str] = Field(default=None, description="Optional hint/context")
    # If you want: max_length_seconds: Optional[int] = None

class VoiceResponse(BaseModel):
    transcript_text: str
    answer_text: str
    audio_file_url: str
    transcript_file_url: Optional[str] = None
