"""Render.com / production entry point.

Use ONE of these start commands on Render:

  gunicorn -w 1 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT
  uvicorn app:app --host 0.0.0.0 --port $PORT

Do NOT use `gunicorn app:server` alone — that serves only the Dash Flask app,
skips FastAPI (/health, /api/*) and skips the steering scheduler lifespan.
"""

from tcams.main import app, dash_app

server = dash_app.server

__all__ = ["app", "dash_app", "server"]
