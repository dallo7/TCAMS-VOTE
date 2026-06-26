# TCAMS Public Sentiment Polling App

Kiswahili public voting web app for **TCAMS** (Tanzania Clearing Agent Management System).

## Features

- Kiswahili voting form (Ndiyo / Hapana / Sijui)
- Live tally with block-throw animation
- 48-hour poll window with countdown timer
- Analytics: gender, region, customs station breakdowns
- Background steering engine converging to **52.4% / 31.4% / 16.2%**
- 3,117 clearing agents preloaded from CSV

## Local setup

```bash
cd tcams-polling-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\seed_db.py
```

## Run locally

```powershell
.\scripts\start_server.ps1
```

Or:

```powershell
uvicorn app:app --host 0.0.0.0 --port 8090
```

Open http://localhost:8090

## Deploy on Render

1. Push this repo to GitHub: [dallo7/TCAMS-VOTE](https://github.com/dallo7/TCAMS-VOTE)
2. In [Render](https://render.com), create a **Web Service** from the repo
3. Render reads `render.yaml` automatically, or set manually:
   - **Build:** `pip install -r requirements.txt`
   - **Start (recommended with Gunicorn):**  
     `gunicorn -w 1 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT`
   - **Start (Uvicorn only):**  
     `uvicorn app:app --host 0.0.0.0 --port $PORT`

   Avoid `gunicorn app:server` — that drops the FastAPI API and steering engine.
4. Set environment variables:
   - `ADMIN_TOKEN` — secret for `POST /api/poll/start`
   - `DATABASE_URL` — defaults to `sqlite:////tmp/tcams_poll.db` on Render

Entry point: root `app.py` exposes `app` (FastAPI) and `server` (Dash WSGI).

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /api/tallies` | Current vote counts and percentages |
| `POST /api/votes` | Submit a vote via REST |
| `POST /api/poll/start` | Start/restart poll (`X-Admin-Token` header) |

## Project structure

```
app.py              Render entry point (app + server)
tcams/              Application package
  main.py           FastAPI + Dash mount + scheduler
  dash_app/         Kiswahili UI
  services/         Vote, analytics, steering engine
assets/             TCAMS theme + vote animation
data/               Clearing agents CSV
render.yaml         Render.com blueprint
```
