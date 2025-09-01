from fastapi import APIRouter
from ..schemas import ImageWorksheetRequest, ImageWorksheetResponse, WorksheetItem
from ..utils.ids import make_id

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/worksheet", response_model=ImageWorksheetResponse)
def generate_worksheet(body: ImageWorksheetRequest):
    # Stubbed response (contract only)
    items = [
        WorksheetItem(type="mcq", q="What is 23 + 19?", options=["32","42","43","44"], answer="42"),
        WorksheetItem(type="short", q="Explain what a food chain is.", rubric="2-3 sentences, example included"),
        WorksheetItem(type="diagram", q="Label the parts of a plant shown.", answer="Root, Stem, Leaf, Flower")
    ]
    return ImageWorksheetResponse(
        worksheet_id=make_id("ws"),
        items=items,
        printable_pdf_url="/files/ws_sample.pdf"
    )
