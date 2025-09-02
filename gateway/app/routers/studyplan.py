from fastapi import APIRouter, HTTPException
from ..schemas import StudyPlanRequest, StudyPlanResponse
from ..utils.ids import make_id
from .. import deps
import httpx

router = APIRouter(prefix="/studyplan", tags=["studyplan"])

@router.post("/from-syllabus", response_model=StudyPlanResponse)
def create_plan(body: StudyPlanRequest):
    """
    Forwards to studyplan-agent. The gateway owns IDs if you want them here,
    but studyplan-agent already creates a plan_id; we keep this simple and accept its response.
    """
    try:
        with httpx.Client(timeout=60) as client:
            r = client.post(f"{deps.STUDYPLAN_URL}/from-syllabus", json=body.model_dump())
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return StudyPlanResponse(**r.json())
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"studyplan-agent unreachable: {e}")
