from fastapi import FastAPI, HTTPException
from .schemas import VoiceRequest, VoiceResponse
from .agent import handle_voice

app = FastAPI(title="voice-agent", version="0.2.0")

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/explain", response_model=VoiceResponse)
def explain(body: VoiceRequest):
    try:
        return handle_voice(body)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"voice-agent error: {e}")
