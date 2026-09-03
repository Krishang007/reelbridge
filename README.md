# ReelBridge

ReelBridge turns a public Instagram Reel URL into a browser-downloadable MP4.
It downloads media with `yt-dlp`, converts incompatible media to QuickTime-
friendly H.264/AAC MP4 with FFmpeg, and compresses oversized files to a 15 MB
target for better sharing compatibility.

## User Flow

```text
Paste Instagram Reel URL
        |
FastAPI -> yt-dlp -> FFmpeg when needed
        |
Download reel.mp4
        |
Share through Discord, WhatsApp, Messages, or another app
```

The app is stateless and does not use a database. Downloaded files are
temporary and deleted after the response. Discord experiments are optional and
are kept under `optional/discord/`.

## Layout

```text
reelbridge/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── reel_service.py
│   └── requirements.txt
├── frontend/
├── Dockerfile
└── .dockerignore
```

## Requirements

- Python 3.12 or newer
- Node.js and npm
- FFmpeg for local development

On macOS:

```bash
brew install ffmpeg
```

## Run Locally

Create and activate the Python environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Start the backend in Terminal 1:

```bash
cd backend
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000` and its documentation is at
`http://127.0.0.1:8000/docs`.

Start the frontend in Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://localhost:5173`, paste a public Instagram
Reel URL, and click **Get Reel**.

The frontend defaults to `http://localhost:8000`. To configure it explicitly:

```bash
cp .env.example .env.local
```

Set this in `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

Run frontend checks with:

```bash
cd frontend
npm run lint
npm run build
```

## Run with Docker

The root Dockerfile builds React, installs FastAPI and FFmpeg, and serves the
frontend and API from one container and one URL.

From the project root:

```bash
docker build -t reelbridge .
docker run --rm --name reelbridge -p 8000:8000 reelbridge
```

Open [http://localhost:8000](http://localhost:8000). The container serves both
the React app and FastAPI from this URL. In Docker mode, React uses the same
origin for the API, so `VITE_API_URL` is not required.

To stop the container:

```bash
docker stop reelbridge
```

## Docker Watch

Use Docker Compose Watch while developing in the single container. Backend
Python changes are synced into the container and Uvicorn reloads them.
Frontend source changes rebuild the image so the new Vite production assets are
served by FastAPI.

Docker Compose Watch requires Compose 2.22 or newer.

From the project root:

```bash
docker compose up --watch
```

Open [http://localhost:8000](http://localhost:8000), edit a file, and refresh
the page if the browser does not update automatically.

Stop Watch with:

```bash
docker compose down
```

Do not run `docker run ...` and `docker compose up --watch` at the same time;
both try to use port `8000`.

## Deploy

Deploy the repository root as one Docker web service. Use the root
`Dockerfile`; do not set `backend/` as the service root. The container reads
the platform-provided `PORT` variable and serves both the React app and API.

## Troubleshooting

- `No module named app`: run Uvicorn from inside `backend/`.
- `ffmpeg not found`: install FFmpeg locally or use Docker.
- `Download failed`: use a public Instagram Reel URL and update `yt-dlp`.
- CORS errors: use `http://localhost:5173` or set `FRONTEND_ORIGIN`.
- Never commit `config.py`, `.env`, `.venv/`, downloaded media, or Discord
  experiment files.

Only download and share content you have permission to use.
