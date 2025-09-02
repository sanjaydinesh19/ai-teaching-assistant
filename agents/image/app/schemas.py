from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class QuestionMix(BaseModel):
    mcq: int = 6
    short: int = 4
    diagram: int = 2

class ImageWorksheetRequest(BaseModel):
    file_id: str
    grade_bands: List[str]
    difficulty_curve: Literal["easy", "easy-to-hard", "balanced"] = "easy-to-hard"
    question_mix: QuestionMix = QuestionMix()

class WorksheetItem(BaseModel):
    type: Literal["mcq","short","diagram"]
    q: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    rubric: Optional[str] = None

class ImageWorksheetResponse(BaseModel):
    worksheet_id: str
    items: List[WorksheetItem]
    printable_pdf_url: str
