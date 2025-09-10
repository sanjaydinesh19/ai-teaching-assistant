from fastapi import FastAPI, HTTPException
from .schemas import StudyPlanRequest, StudyPlanResponse
from .agent import generate_study_plan

app = FastAPI(title="studyplan-agent", version="0.2.0")

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.post("/from-syllabus", response_model=StudyPlanResponse)
def from_syllabus(body: StudyPlanRequest):
    try:
        return generate_study_plan(body)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"studyplan error: {e}")
