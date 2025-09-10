from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class StudyPlanRequest(BaseModel):
    file_id: str
    grades: List[str]
    duration_weeks: int = Field(gt=0, le=52)
    constraints: Optional[Dict[str, Any]] = None
    target_language: str = Field(default="en", description="BCP-47 like 'en', 'hi', 'ta'")

class WeeklyItem(BaseModel):
    week: int
    topics: List[str]
    activities: List[str]
    assessment: str
    homework: Optional[str] = None
    resources: List[Dict[str, str]] = []  # {title, platform, search_query}

class StudyPlanResponse(BaseModel):
    plan_id: str
    grades: List[str]
    weeks: int
    target_language: str
    overview: str
    weekly_outline: List[WeeklyItem]
    printable_file_url: str  # can be .pdf or .md depending on font availability
