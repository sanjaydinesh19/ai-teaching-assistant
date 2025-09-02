from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import studyplan, image, voice
import os

app = FastAPI(
    title="Teaching Assistant Gateway",
    version="0.3.0",
    description="Central API routing and contracts for frontend ⇄ agents."
)

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

# Routers
app.include_router(studyplan.router)
app.include_router(image.router)
app.include_router(voice.router)

# Serve static files (PDFs and MP3s) from _filestore
FILE_ROOT = os.environ.get("FILE_STORE", "/data")
app.mount("/files", StaticFiles(directory=FILE_ROOT), name="files")
