import csv

from sqlalchemy.orm import Session

from tcams.config import CSV_PATH
from tcams.models import Agent


def seed_agents(db: Session) -> int:
    if db.query(Agent).count() > 0:
        return db.query(Agent).count()

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    inserted = 0
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            agent = Agent(
                sn=int(row["SN"]),
                name=row["Name"].strip(),
                gender=row["Gender"].strip(),
                region=row["Region"].strip(),
                customs_station=row["Nearest Port / Border Customs Station"].strip(),
                used_for_steering=False,
            )
            db.add(agent)
            inserted += 1

    db.commit()
    return inserted
