import os, time, random, string
from fastapi import FastAPI, HTTPException
from .schemas import StudyPlanRequest, StudyPlanResponse
from .tools import syllabus_text_from_file_id
from .agent import generate_studyplan

app = FastAPI(title="studyplan-agent", version="0.1.0")

def make_id(prefix: str) -> str:
    ts = str(int(time.time()))
    rnd = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{prefix}_{ts}{rnd}"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/from-syllabus", response_model=StudyPlanResponse)
def from_syllabus(body: StudyPlanRequest):
    try:
        syllabus_text = syllabus_text_from_file_id(body.file_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read syllabus: {e}")

    plan_id = make_id("sp")
    try:
        resp = generate_studyplan(syllabus_text, body, plan_id)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planner error: {e}")
