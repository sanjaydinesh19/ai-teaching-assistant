from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import studyplan, image, voice,upload
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI(
    title="Teaching Assistant Gateway",
    version="0.3.0",
    description="Central API routing and contracts for frontend ⇄ agents."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

# Routers
app.include_router(studyplan.router)
app.include_router(image.router)
app.include_router(voice.router)
app.include_router(upload.router)

# Serve static files (PDFs and MP3s) from _filestore
FILE_ROOT = os.environ.get("FILE_STORE", "/data")
app.mount("/files", StaticFiles(directory=FILE_ROOT), name="files")
