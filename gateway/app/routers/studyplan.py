from fastapi import APIRouter, HTTPException
from ..schemas import StudyPlanRequest, StudyPlanResponse
from ..utils.ids import make_id
from .. import deps
import httpx

router = APIRouter(prefix="/studyplan", tags=["studyplan"])

@router.post("/from-syllabus")
def create_plan(body: StudyPlanRequest):
    try:
        with httpx.Client(timeout=60) as client:
            r = client.post(f"{deps.STUDYPLAN_URL}/from-syllabus", json=body.model_dump())
            if r.status_code != 200:
                print("Studyplan-agent error:", r.text)
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return r.json()  
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"studyplan-agent unreachable: {e}")

