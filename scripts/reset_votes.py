"""Clear all vote records (charts/tallies) while keeping agents and poll schedule."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tcams.database import SessionLocal
from tcams.models import Agent
from tcams.services.vote_service import get_tallies, reset_votes


def main() -> None:
    db = SessionLocal()
    try:
        deleted = reset_votes(db)
        after = get_tallies(db)
        agents = db.query(Agent).count()
        print(f"Cleared {deleted} vote(s). Agents preserved: {agents}.")
        print(f"Charts reset to: {after['counts']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
