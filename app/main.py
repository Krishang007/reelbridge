from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from app.reel_service import download_reel

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# create a fastapi swagger app 
app = FastAPI(
    title="ReelBridge",
    version="0.1.0"
)


class ReelRequest(BaseModel):
    url: HttpUrl
    action: Literal["download", "discord", "whatsapp", "text"] = "download"

@app.get("/")
def root():
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
        video_path = download_reel(url)

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
