from fastapi import APIRouter
from ..schemas import StudyPlanRequest, StudyPlanResponse, WeeklyItem
from ..utils.ids import make_id

router = APIRouter(prefix="/studyplan", tags=["studyplan"])

@router.post("/from-syllabus", response_model=StudyPlanResponse)
def create_plan(body: StudyPlanRequest):
    # Stubbed response (contract only)
    weeks = [
        WeeklyItem(week=1, topics=["Numbers up to 1000"], outcomes=["Place value"], checks=["Exit ticket"]),
        WeeklyItem(week=2, topics=["Addition & Subtraction"], outcomes=["Column addition"], checks=["1-minute quiz"]),
    ]
    return StudyPlanResponse(
        plan_id=make_id("sp"),
        overview="Unit-wise spiral plan aligned to multi-grade pacing.",
        weekly_outline=weeks,
        resources=[{"type": "worksheet", "agent": "image-agent", "template": "mcq-3-levels"}]
    )
