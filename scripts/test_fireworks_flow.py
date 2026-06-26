"""Smoke test for vote success + fireworks wiring (no DB writes)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    fireworks_js = ROOT / "assets" / "fireworks.js"
    if not fireworks_js.is_file():
        errors.append("missing assets/fireworks.js")
    else:
        text = fireworks_js.read_text(encoding="utf-8")
        if "window.tcamsFireworks" not in text:
            errors.append("fireworks.js does not define window.tcamsFireworks")

    css = (ROOT / "assets" / "vote-animation.css").read_text(encoding="utf-8")
    for needle in ("tcams-fireworks", "tcams-firework-particle", "tcams-alert--celebrate"):
        if needle not in css:
            errors.append(f"vote-animation.css missing {needle}")

    from tcams.dash_app import i18n_sw as sw

    msg = sw.vote_success_message("Amina Hassan")
    if "Amina Hassan" not in msg:
        errors.append(f"vote_success_message unexpected: {msg!r}")

    from tcams.main import dash_app

    callback_ids = set(dash_app.callback_map.keys())
    if not any("celebration-trigger" in cid for cid in callback_ids):
        errors.append("no callback listens to celebration-trigger")
    if not any("animation-trigger" in cid for cid in callback_ids):
        errors.append("no callback listens to animation-trigger")

    layout_str = str(dash_app.layout)
    for needle in ("celebration-trigger", "celebration-layer", "vote-feedback"):
        if needle not in layout_str:
            errors.append(f"layout missing {needle}")

    with dash_app.server.test_client() as client:
        resp = client.get("/")
        if resp.status_code != 200:
            errors.append(f"GET / returned {resp.status_code}")
        elif "fireworks.js" not in resp.get_data(as_text=True):
            errors.append("index page does not reference fireworks.js asset")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: fireworks flow wiring OK")
    print(f"  - vote_success_message: {msg}")
    print(f"  - callbacks registered: {len(callback_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
