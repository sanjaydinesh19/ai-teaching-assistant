import os, json, base64
from openai import OpenAI
from .schemas import ImageWorksheetRequest, ImageWorksheetResponse, WorksheetItem
from .pdf import render_pdf

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
OPENAI_MODEL = os.environ.get("OPENAI_MODEL","gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a worksheet generator. "
    "Given a textbook page image, generate age-appropriate questions:\n"
    "- Use 'mcq', 'short', or 'diagram' types\n"
    "- Provide answer keys (and rubric for short/diagram)\n"
    "- Keep JSON strictly valid.\n"
    "Always return a JSON object with an 'items' key."
    "Each item must have\n:"
    '- type: "mcq" | "short" | "diagram"'
    '- q: string'
    '- options (if mcq): list of strings'
    '- answer: string (for mcq/diagram)'
    '- rubric (for short/diagram): short guidance'
    'Return nothing else.'
)

def encode_image(path: str) -> str:
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()

def generate_worksheet(req: ImageWorksheetRequest, file_path: str, worksheet_id: str) -> ImageWorksheetResponse:
    img_b64 = encode_image(file_path)
    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":[
            {"type":"text","text":(
                f"Grades: {req.grade_bands}\n"
                f"Difficulty: {req.difficulty_curve}\n"
                f"Question mix: {req.question_mix.dict()}\n\n"
                "Generate a JSON list of questions."
            )},
            {"type":"image_url","image_url":{"url":f"data:image/png;base64,{img_b64}"}}
        ]}
    ]
    resp = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=messages,
    temperature=0.3,
    response_format={"type": "json_object"}
    )
    content = resp.choices[0].message.content
    json_obj = json.loads(content)

    # Handle both dict-with-items and plain list
    if isinstance(json_obj, dict) and "items" in json_obj:
        items_raw = json_obj["items"]
    elif isinstance(json_obj, list):
        items_raw = json_obj
    else:
        items_raw = []

    items = [WorksheetItem(**q) for q in items_raw if isinstance(q, dict)]

    pdf_path = render_pdf(items, worksheet_id)
    return ImageWorksheetResponse(
        worksheet_id=worksheet_id,
        items=items,
        printable_pdf_url=f"/files/{os.path.basename(pdf_path)}"
    )
