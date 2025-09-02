import os, time, random, string
from fastapi import FastAPI, HTTPException
from .schemas import ImageWorksheetRequest, ImageWorksheetResponse
from .agent import generate_worksheet

FILE_STORE = os.environ.get("FILE_STORE","/data")
app = FastAPI(title="image-agent", version="0.1.0")

def make_id(prefix="ws"):
    ts=str(int(time.time()))
    rnd="".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
    return f"{prefix}_{ts}{rnd}"

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/worksheet", response_model=ImageWorksheetResponse)
def worksheet(body: ImageWorksheetRequest):
    path = os.path.join(FILE_STORE, f"{body.file_id}.png")
    if not os.path.exists(path):
        raise HTTPException(404, f"Image not found: {path}")
    worksheet_id = make_id()
    try:
        return generate_worksheet(body, path, worksheet_id)
    except Exception as e:
        raise HTTPException(500, f"Worksheet generation failed: {e}")
