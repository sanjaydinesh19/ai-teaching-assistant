import time, random, string
from fastapi import FastAPI, HTTPException
from .schemas import VoiceAskRequest, VoiceAskResponse
from .agent import process_voice

app = FastAPI(title="voice-agent", version="0.1.0")

def make_id(prefix="ans"):
    ts=str(int(time.time()))
    rnd="".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
    return f"{prefix}_{ts}{rnd}"

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/ask", response_model=VoiceAskResponse)
def ask(body: VoiceAskRequest):
    ans_id = make_id()
    try:
        return process_voice(body, ans_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Voice agent error: {e}")
