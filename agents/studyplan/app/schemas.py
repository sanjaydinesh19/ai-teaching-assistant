from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

class StudyPlanRequest(BaseModel):
    file_id: str
    grades: List[str]
    duration_weeks: int = Field(..., ge=1, le=52)
    constraints: Optional[Dict[str, object]] = None

class WeeklyItem(BaseModel):
    week: int
    topics: List[str]
    outcomes: List[str]
    checks: Optional[List[str]] = None

class StudyPlanResponse(BaseModel):
    plan_id: str
    overview: str
    weekly_outline: List[WeeklyItem]
    resources: List[Dict[str, str]] = []
