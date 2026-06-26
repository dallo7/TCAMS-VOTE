import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = BASE_DIR / "tcams_poll.db"
CSV_PATH = DATA_DIR / "tanzania_clearing_agents.csv"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "tcams-admin-start")
APP_VERSION = "2026.06.29-launch"

TZ_EAT = timezone(timedelta(hours=3))


def _eat(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, second, tzinfo=TZ_EAT)


# Uchaguzi: Jumatatu 29 Juni 2026 hadi 8 Julai 2026 (EAT)
POLL_START_AT = _eat(2026, 6, 29)
POLL_END_AT = _eat(2026, 7, 8, 23, 59, 59)
POLL_DURATION_HOURS = 48

TARGET_YES_PCT = 52.4
TARGET_NO_PCT = 31.4
TARGET_NOT_SURE_PCT = 16.2

INTERVALS_MIN = [1, 2, 3, 4, 7, 10, 16, 35, 57]
GAP_TARGETS_PP = [19, 14, 20, 11]
FINAL_PHASE_HOURS = 9
MAX_GAP_TRIGGER = 26
MAX_GAP_STEADY = 14

STEERING_TICK_SECONDS = 60
UI_REFRESH_MS = 3000
