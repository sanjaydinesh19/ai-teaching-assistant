from fastapi import APIRouter, HTTPException
from ..schemas import ImageWorksheetRequest, ImageWorksheetResponse
from .. import deps
import httpx

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/worksheet", response_model=ImageWorksheetResponse)
def generate_worksheet(body: ImageWorksheetRequest):
    try:
        with httpx.Client(timeout=90) as client:
            r = client.post(f"{deps.IMAGE_URL}/worksheet", json=body.model_dump())
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return ImageWorksheetResponse(**r.json())
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"image-agent unreachable: {e}")
