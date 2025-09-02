from fastapi import APIRouter, HTTPException
from ..schemas import VoiceAskRequest, VoiceAskResponse
from .. import deps
import httpx

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/ask", response_model=VoiceAskResponse)
def voice_ask(body: VoiceAskRequest):
    try:
        with httpx.Client(timeout=120) as client:
            r = client.post(f"{deps.VOICE_URL}/ask", json=body.model_dump())
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return VoiceAskResponse(**r.json())
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"voice-agent unreachable: {e}")
