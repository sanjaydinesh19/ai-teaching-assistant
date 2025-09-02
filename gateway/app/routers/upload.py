from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os, shutil

router = APIRouter(prefix="/upload", tags=["upload"])

FILE_ROOT = os.environ.get("FILE_STORE", "/data")

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    file_id: str = Form(...)  # e.g., upload-123 (no extension)
):
    # Save to /data/<file_id>.<ext> based on content_type or filename
    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    elif file.content_type == "application/pdf":
        ext = ".pdf"
    elif file.content_type in ("image/png", "image/x-png"):
        ext = ".png"
    elif file.content_type in ("image/jpeg", "image/jpg"):
        ext = ".jpg"
    elif file.content_type in ("audio/wav", "audio/x-wav"):
        ext = ".wav"
    elif file.content_type in ("audio/mpeg", "audio/mp3"):
        ext = ".mp3"

    if not ext:
        raise HTTPException(415, f"Unsupported file type: {file.content_type}")

    os.makedirs(FILE_ROOT, exist_ok=True)
    dest = os.path.join(FILE_ROOT, f"{file_id}{ext}")

    try:
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(500, f"Failed to save file: {e}")

    return {"ok": True, "file_id": file_id, "saved_as": f"/files/{file_id}{ext}"}
