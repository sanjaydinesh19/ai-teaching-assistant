from fastapi import FastAPI, HTTPException
from .schemas import WorksheetRequest, WorksheetResponse
from .agent import build_worksheets

app = FastAPI(title="image-agent", version="0.2.0")

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.post("/worksheet", response_model=WorksheetResponse)
def worksheet(body: WorksheetRequest):
    try:
        return build_worksheets(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"image-agent error: {e}")
