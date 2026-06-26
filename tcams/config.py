import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = BASE_DIR / "tcams_poll.db"
CSV_PATH = DATA_DIR / "tanzania_clearing_agents.csv"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "tcams-admin-start")
APP_VERSION = "2026.06.26-celebrate-v2"
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
