from fastapi import APIRouter, HTTPException, Request
from .. import deps
import httpx

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/worksheet")
async def generate_worksheet(request: Request):
    body = await request.json()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{deps.IMAGE_URL}/worksheet", json=body)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"image-agent unreachable: {e}")
