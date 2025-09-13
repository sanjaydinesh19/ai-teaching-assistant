from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Literal

# ===== Studyplan =====
class StudyPlanRequest(BaseModel):
    file_id: str = Field(..., description="Upload/file handle for the syllabus PDF")
    grades: List[str] = Field(..., description='e.g., ["3","4","5"]')
    duration_weeks: int = Field(..., ge=1, le=52)
    constraints: Optional[Dict[str, object]] = Field(
        default=None,
        description='e.g., {"per_day_minutes": 35, "weekdays": ["Mon","Wed","Fri"]}'
    )
    target_language: str = Field(default="en", description="Target language code, e.g., 'en', 'hi', 'ta'")

class WeeklyItem(BaseModel):
    week: int
    topics: List[str]
    outcomes: List[str]
    checks: Optional[List[str]] = None  # formative checks

class StudyPlanResponse(BaseModel):
    plan_id: str
    overview: str
    weekly_outline: List[WeeklyItem]
    resources: List[Dict[str, str]] = Field(
        default_factory=list,
        description='Pointers to follow-ups, e.g., {"type":"worksheet","agent":"image-agent","template":"mcq-3-levels"}'
    )

# ===== Image → Worksheet =====
class QuestionMix(BaseModel):
    mcq: int = 6
    short: int = 4
    diagram: int = 2

class ImageWorksheetRequest(BaseModel):
    file_id: str = Field(..., description="Upload/file handle for textbook page(s)")
    grade_bands: List[str] = Field(..., description='e.g., ["3-4", "5-6"]')
    difficulty_curve: Literal["easy", "easy-to-hard", "balanced"] = "easy-to-hard"
    question_mix: QuestionMix = QuestionMix()

class WorksheetItem(BaseModel):
    type: Literal["mcq", "short", "diagram"]
    q: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    rubric: Optional[str] = None

class ImageWorksheetResponse(BaseModel):
    worksheet_id: str
    items: List[WorksheetItem]
    printable_pdf_url: str

# ===== Voice Q&A =====
class VoiceAskRequest(BaseModel):
    audio_file_id: str
    level: str = Field(..., description="e.g., 'grade-5'")
    visual_format: Literal["board-notes", "steps", "story"] = "board-notes"
    max_seconds: int = Field(90, ge=15, le=180)

class VoiceAskResponse(BaseModel):
    transcript: str
    explanation: str
    audio_url: str

# --- Voice Agent Schemas ---
class VoiceRequest(BaseModel):
    file_id: str
    target_language: str = "en"
    topic_hint: Optional[str] = None


class VoiceResponse(BaseModel):
    transcript: str
    answer_text: str
    answer_audio_url: str
