from fastapi import APIRouter
from ..schemas import VoiceAskRequest, VoiceAskResponse
from ..utils.ids import make_id

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/ask", response_model=VoiceAskResponse)
def voice_ask(body: VoiceAskRequest):
    # Stubbed response (contract only)
    return VoiceAskResponse(
        transcript="Why do shadows change length during the day?",
        explanation="Because the Sun’s apparent position changes, causing different angles of light.",
        audio_url="/files/ans_sample.mp3"
    )
