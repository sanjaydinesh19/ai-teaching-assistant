from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any

Difficulty = Literal["easy", "medium", "hard"]

class WorksheetRequest(BaseModel):
    # Multiple uploaded files (by file_id from /upload)
    file_ids: List[str] = Field(..., description="List of uploaded file IDs without extension")
    grade_bands: Optional[List[str]] = Field(default=None, description='e.g., ["3-4"] or ["5"]')
    num_sets: int = Field(..., gt=0, le=10, description="How many different sets to generate")
    difficulty_levels: List[Difficulty] = Field(..., description='Either length==num_sets or length==1 (broadcast)')
    questions_per_set: int = Field(..., gt=1, le=50)
    question_mix: Optional[Dict[str, int]] = Field(default=None, description='e.g., {"mcq":3,"short":2,"diagram":1}')
    target_language: str = Field(default="en")

class WorksheetItem(BaseModel):
    type: str
    q: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    rubric: Optional[str] = None

class WorksheetSetResponse(BaseModel):
    set_no: int
    difficulty: Difficulty
    items: List[WorksheetItem]
    printable_pdf_url: str

class WorksheetResponse(BaseModel):
    worksheet_id: str
    sets: List[WorksheetSetResponse]
