"""Smoke test for vote success + fireworks wiring (no DB writes)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    js = (ROOT / "assets" / "vote-animation.js").read_text(encoding="utf-8")
    for needle in ("tcamsFireworks", "tcamsCelebrateVote", "tcamsAnimateVote"):
        if needle not in js:
            errors.append(f"vote-animation.js missing {needle}")

    css = (ROOT / "assets" / "vote-animation.css").read_text(encoding="utf-8")
    for needle in ("tcams-fireworks", "tcams-firework-particle", "tcams-alert--celebrate"):
        if needle not in css:
            errors.append(f"vote-animation.css missing {needle}")

    from tcams.dash_app import i18n_sw as sw

    msg = sw.vote_success_message("Amina Hassan")
    if "Amina Hassan" not in msg:
        errors.append(f"vote_success_message unexpected: {msg!r}")

    from starlette.testclient import TestClient
    from tcams.config import APP_VERSION
    from tcams.main import app, dash_app

    callback_ids = set(dash_app.callback_map.keys())
    if not any("animation-trigger" in cid for cid in callback_ids):
        errors.append("no callback listens to animation-trigger")

    layout_str = str(dash_app.layout)
    for needle in ("vote-feedback", "animation-layer"):
        if needle not in layout_str:
            errors.append(f"layout missing {needle}")

    with dash_app.server.test_client() as client:
        resp = client.get("/")
        if resp.status_code != 200:
            errors.append(f"GET / returned {resp.status_code}")
        elif "vote-animation.js" not in resp.get_data(as_text=True):
            errors.append("index page does not reference vote-animation.js")

    with TestClient(app) as client:
        health = client.get("/health")
        if health.status_code != 200:
            errors.append(f"GET /health returned {health.status_code}")
        elif APP_VERSION not in health.text:
            errors.append("health endpoint missing APP_VERSION")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: fireworks flow wiring OK")
    print(f"  - vote_success_message: {msg}")
    print(f"  - app_version: {APP_VERSION}")
    print(f"  - callbacks registered: {len(callback_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
