from pathlib import Path
from typing import Literal
import os

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from app.reel_service import download_reel, prepare_reel
from fastapi.middleware.cors import CORSMiddleware

# create a fastapi swagger app 
app = FastAPI(
    title="ReelBridge",
    version="0.1.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]

FRONTEND_DIST = Path(
    os.getenv("FRONTEND_DIST", "frontend/dist")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=assets_dir),
        name="assets",
    )

class ReelRequest(BaseModel):
    url: HttpUrl
    action: Literal["download", "discord", "whatsapp", "text"] = "download"

@app.get("/")
def root():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return {
        "name": "ReelBridge",
        "status": "running"
    }

@app.post("/reel/download")
def download(
    request: ReelRequest,
    background_tasks: BackgroundTasks
):
    url = str(request.url)

    if "instagram.com" not in request.url.host:
        raise HTTPException(
            status_code=400,
            detail="Only Instagram URLs are supported."
        )

    try:
        video_path = prepare_reel(download_reel(url))

        background_tasks.add_task(
            delete_file,
            video_path
        )

        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename="reel.mp4"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {e}"
        )

def delete_file(path: Path):
    if path.exists():
        path.unlink()
        print(f"Deleted: {path}")
