from fastapi import APIRouter, HTTPException, Request
from .. import deps
import httpx

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/explain")
async def explain(request: Request):
    body = await request.json()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{deps.VOICE_URL}/explain", json=body)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"voice-agent unreachable: {e}")
