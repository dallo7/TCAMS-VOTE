"""Render.com / production entry point."""

from tcams.main import app, dash_app

server = dash_app.server

__all__ = ["app", "dash_app", "server"]
