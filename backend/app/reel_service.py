from pathlib import Path
import subprocess
import uuid
import yt_dlp

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
# Keep output below WhatsApp's 16 MB forwarded-video limit.
MAX_FILE_SIZE = 15 * 1024 * 1024


def _codec_name(video_path: Path, stream_selector: str) -> str:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            stream_selector,
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def download_reel(url: str) -> Path:
    file_id = uuid.uuid4().hex
    output_template = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

    options = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = Path(ydl.prepare_filename(info))

    if not downloaded_file.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{file_id}.*"))
        if not candidates:
            raise FileNotFoundError("yt-dlp did not produce a video file")
        downloaded_file = next(
            (path for path in candidates if path.suffix.lower() == ".mp4"),
            candidates[0],
        )

    return downloaded_file


def prepare_reel(video_path: Path) -> Path:
    """Return a browser-friendly MP4, compressing only oversized files."""
    is_mp4 = video_path.suffix.lower() == ".mp4"
    is_small_enough = video_path.stat().st_size <= MAX_FILE_SIZE
    video_codec = _codec_name(video_path, "v:0")
    audio_codec = _codec_name(video_path, "a:0")
    is_quicktime_compatible = (
        video_codec == "h264" and audio_codec in {"aac", ""}
    )

    if is_mp4 and is_small_enough and is_quicktime_compatible:
        return video_path

    compressed_path = video_path.with_name(f"{video_path.stem}-compressed.mp4")
    for crf in (28, 32, 36, 40):
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            "scale='min(720,iw)':-2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "fast",
            "-crf",
            str(crf),
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(compressed_path),
        ]

        subprocess.run(command, check=True, capture_output=True, text=True)
        if compressed_path.stat().st_size <= MAX_FILE_SIZE:
            video_path.unlink()
            return compressed_path

    compressed_path.unlink(missing_ok=True)
    raise ValueError("Could not compress the Reel below 15 MB")
