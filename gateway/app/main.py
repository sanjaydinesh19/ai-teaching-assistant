from fastapi import FastAPI
from .routers import studyplan, image, voice

app = FastAPI(
    title="Teaching Assistant Gateway",
    version="0.1.0",
    description="Central API routing and contracts for frontend ⇄ agents."
)

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

# Routers (contracts)
app.include_router(studyplan.router)
app.include_router(image.router)
app.include_router(voice.router)
