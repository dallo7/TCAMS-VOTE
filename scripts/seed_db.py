"""Seed the TCAMS polling database with clearing agents."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tcams.database import Base, SessionLocal, engine
from tcams.seed import seed_agents


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_agents(db)
        print(f"Seeded {count} agents.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
