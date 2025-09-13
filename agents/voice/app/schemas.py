from pydantic import BaseModel, Field
from typing import Optional

class VoiceRequest(BaseModel):
    file_id: str
    target_language: str = "en"
    tts_voice: str = "alloy"
    tts_speed: float = 1.0
    topic_hint: Optional[str] = None

class VoiceResponse(BaseModel):
    transcript: str
    answer_text: str
    answer_audio_url: str
    transcript_file_url: Optional[str] = None
