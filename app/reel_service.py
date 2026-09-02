from pathlib import Path
import uuid
import yt_dlp

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def download_reel(url: str) -> Path:
    file_id = uuid.uuid4().hex
    output_template = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = Path(ydl.prepare_filename(info))

    return downloaded_file