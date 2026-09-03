# ReelBridge Learning Guide

This document explains the engineering concepts used in ReelBridge. Read it
alongside the source code and try to explain each function before changing it.

## Official Online Documentation

Use these links as the primary learning material for the technologies in this
project. The links are ordered from the user interface outward to deployment.

1. [React Learn](https://react.dev/learn) covers components, JSX, events, and
   the basic React mental model.
2. [Managing State in React](https://react.dev/learn/managing-state) explains
   state variables, controlled inputs, and how state changes trigger renders.
3. [MDN Forms](https://developer.mozilla.org/en-US/docs/Learn/Forms) explains
   browser forms, inputs, submit events, and validation.
4. [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
   explains how the frontend calls the FastAPI endpoint.
5. [MDN Blob](https://developer.mozilla.org/en-US/docs/Web/API/Blob) and
   [URL.createObjectURL()](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)
   explain how the browser handles the returned MP4 bytes.
6. [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) introduces the
   backend framework and its routing model.
7. [FastAPI Request Bodies](https://fastapi.tiangolo.com/tutorial/body/),
   [CORS](https://fastapi.tiangolo.com/tutorial/cors/), and
   [Custom Responses](https://fastapi.tiangolo.com/advanced/custom-response/)
   map directly to ReelBridge's request validation, browser access, and file
   downloads.
8. [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/) explains
   the validation performed by `ReelRequest` and `HttpUrl`.
9. [yt-dlp](https://github.com/yt-dlp/yt-dlp) documents the Python API, format
   selection, output templates, and extractor errors.
10. [FFmpeg Documentation](https://ffmpeg.org/documentation.html), the
    [FFmpeg command reference](https://ffmpeg.org/ffmpeg.html), and the
    [ffprobe reference](https://ffmpeg.org/ffprobe.html) explain conversion,
    compression, and media inspection.
11. [Vite Environment Variables](https://vite.dev/guide/env-and-mode) and
    [Vite Production Builds](https://vite.dev/guide/build) explain
    `VITE_API_URL` and the frontend assets copied into Docker.
12. [Dockerfile Reference](https://docs.docker.com/reference/dockerfile/),
    [Multi-stage Builds](https://docs.docker.com/get-started/docker-concepts/building-images/multi-stage-builds/),
    and [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/)
    explain the one-container build and development workflow.
13. [Render Web Services](https://render.com/docs/web-services) and
    [Deploying FastAPI on Render](https://render.com/docs/deploy-fastapi)
    explain how to run the Docker container online.

The goal is not to memorize every API. For each link, understand the small
part used by the matching source file below, then change one thing and observe
the result.

## Complete Request Flow

```text
User pastes a Reel URL
        |
React submits JSON with fetch()
        |
FastAPI validates the request
        |
yt-dlp downloads the media
        |
ffprobe checks codecs and file size
        |
FFmpeg converts or compresses when needed
        |
FastAPI returns an MP4 FileResponse
        |
React receives a Blob and downloads reel.mp4
```

## Frontend

File: `frontend/src/App.jsx`

### React state

```js
const [url, setUrl] = useState('')
```

Learn:

- [Component state and controlled inputs](https://react.dev/learn/managing-state)
- [Updating state from events](https://react.dev/learn/responding-to-events)
- [Re-rendering when state changes](https://react.dev/learn/state-a-components-memory)

The app stores the URL, loading state, error message, and success message.

### Form submission

```js
async function handleSubmit(event) {
```

Learn:

- [Preventing default form navigation](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault)
- Async functions and `await`
- Managing loading and error states
- Cleaning up state with `finally`

### HTTP requests

```js
fetch(`${API_URL}/reel/download`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url, action: 'download' }),
})
```

Learn:

- [HTTP methods and requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [JSON request bodies with Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- API URLs
- Response status codes
- Browser/backend communication

### Blob downloads

```js
const videoBlob = await response.blob()
const downloadUrl = URL.createObjectURL(videoBlob)
```

Learn:

- [Binary responses and Blob objects](https://developer.mozilla.org/en-US/docs/Web/API/Blob)
- [Temporary browser object URLs](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)
- Programmatic downloads
- [Releasing browser memory with `URL.revokeObjectURL`](https://developer.mozilla.org/en-US/docs/Web/API/URL/revokeObjectURL_static)

## Backend

File: `backend/app/main.py`

### FastAPI application

```python
app = FastAPI(title="ReelBridge", version="0.1.0")
```

Learn:

- [FastAPI application initialization](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Automatic API documentation](https://fastapi.tiangolo.com/features/)
- [Path operation routing](https://fastapi.tiangolo.com/tutorial/first-steps/)

### Pydantic validation

```python
class ReelRequest(BaseModel):
    url: HttpUrl
    action: Literal["download", "discord", "whatsapp", "text"] = "download"
```

Learn:

- [FastAPI type-driven validation](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic model validation](https://docs.pydantic.dev/latest/concepts/models/)
- [Python `Literal` types](https://docs.python.org/3/library/typing.html#typing.Literal)
- Rejecting malformed URLs with `HttpUrl`

### API route

```python
@app.post("/reel/download")
```

Learn:

- [FastAPI POST routes](https://fastapi.tiangolo.com/tutorial/first-steps/)
- Reading validated request data
- Returning successful and failed HTTP responses
- Separating route logic from media-processing logic

### CORS

The browser treats different ports as different origins. CORS allows the local
React server to call FastAPI during development.

The `FRONTEND_ORIGIN` environment variable allows the production origin to be
configured without changing Python code.

Learn with the [FastAPI CORS guide](https://fastapi.tiangolo.com/tutorial/cors/)
and [MDN's same-origin policy explanation](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy).

### FileResponse and cleanup

```python
return FileResponse(
    path=video_path,
    media_type="video/mp4",
    filename="reel.mp4",
)
```

Learn:

- [Sending files with FileResponse](https://fastapi.tiangolo.com/advanced/custom-response/)
- MIME types
- Download filenames
- Temporary-file cleanup after a response

## Media Processing

File: `backend/app/reel_service.py`

### yt-dlp

```python
with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(url, download=True)
```

Learn:

- [yt-dlp's Python embedding documentation](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp)
- Download output templates
- Selecting media formats
- Handling extractor failures

### Path and file discovery

```python
DOWNLOAD_DIR = Path("downloads")
```

Learn:

- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- Temporary files
- File extensions
- Checking whether a file exists
- Reading file size with `stat()`

### Codec compatibility

`ffprobe` checks the internal codec instead of trusting the filename. A file can
be named `.mp4` while containing HEVC or AV1 video that QuickTime cannot play.

ReelBridge converts incompatible media to:

- H.264 video
- AAC audio
- `yuv420p` pixel format
- Fast-start MP4 metadata

### FFmpeg subprocesses

```python
subprocess.run(command, check=True, capture_output=True, text=True)
```

Learn:

- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- Passing arguments safely as a list
- Detecting command failures
- Capturing diagnostic output

### File-size policy

The current target is 15 MB:

```python
MAX_FILE_SIZE = 15 * 1024 * 1024
```

Files that are already compatible and under the limit skip FFmpeg. Other files
are compressed with progressively stronger settings until they fit the target.

## Docker

File: `Dockerfile`

The Dockerfile uses two build stages:

1. Node builds the React frontend.
2. Python runs FastAPI and includes FFmpeg.

This creates one container that serves the React app and API from one URL:

```text
http://localhost:8000
```

Learn with the [Dockerfile reference](https://docs.docker.com/reference/dockerfile/),
[Docker multi-stage build guide](https://docs.docker.com/get-started/docker-concepts/building-images/multi-stage-builds/),
and [Compose Watch guide](https://docs.docker.com/compose/how-tos/file-watch/).

## Deployment And Configuration

### Environment variables

`VITE_API_URL`, `FRONTEND_ORIGIN`, `FRONTEND_DIST`, and `PORT` let the same code
run locally, in Docker, and on Render without hardcoding deployment values.

Learn with [Vite environment variables](https://vite.dev/guide/env-and-mode),
[Docker environment variables](https://docs.docker.com/compose/how-tos/environment-variables/),
and [Render environment variables](https://render.com/docs/configure-environment-variables).

### Stateless architecture

ReelBridge does not use a database. Each request downloads, processes, returns,
and deletes a temporary file. This is suitable for the current single-request
workflow, but a database or job queue would be needed for user accounts,
history, retries, or long-running background jobs.

Learn about [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
before changing cleanup or adding asynchronous processing.

Learn:

- Reproducible environments
- Multi-stage builds
- Installing system dependencies
- Container ports
- Production process commands

## Docker Compose Watch

File: `compose.yaml`

```bash
docker compose up --watch
```

Backend changes sync into the running container. Frontend changes trigger an
image rebuild because the React app is compiled into static files.

Learn:

- Development containers
- File synchronization
- Automatic rebuilds
- Port mapping
- Difference between development and production commands

## Environment Configuration

File: `frontend/.env.example`

```env
VITE_API_URL=http://localhost:8000
```

Frontend variables prefixed with `VITE_` are included in the browser build, so
they must never contain secrets.

Backend secrets belong in ignored local configuration or hosting-provider
environment variables. Never commit bot tokens or API keys.

## Suggested Exercises

1. Change the success message in `App.jsx`.
2. Add a visible file-size message after the download.
3. Add a `GET /health` endpoint.
4. Add logging for the downloaded file size.
5. Change the compression target and observe the result.
6. Add a frontend API error for non-Instagram URLs.
7. Edit a backend file while `docker compose up --watch` is running.
8. Build the image and open `http://localhost:8000` without running Vite.

## Commands

Local backend:

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload
```

Local frontend:

```bash
cd frontend
npm run dev
```

Checks:

```bash
cd frontend
npm run lint
npm run build
```

Docker:

```bash
docker compose up --watch
```
