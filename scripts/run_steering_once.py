"""Run one steering tick manually for testing."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tcams.services.steering_engine import steering_tick


def main() -> None:
    steering_tick()
    print("Steering tick completed.")


if __name__ == "__main__":
    main()
