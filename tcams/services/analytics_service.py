from sqlalchemy import func
from sqlalchemy.orm import Session

from tcams.models import Vote


def get_analytics(db: Session) -> dict:
    total = db.query(func.count(Vote.id)).scalar() or 0

    gender_rows = (
        db.query(Vote.gender, func.count(Vote.id))
        .group_by(Vote.gender)
        .all()
    )
    gender_counts = {gender: count for gender, count in gender_rows}
    male = gender_counts.get("Male", 0)
    female = gender_counts.get("Female", 0)
    gender_total = male + female or 1

    top_region_row = (
        db.query(Vote.region, func.count(Vote.id).label("cnt"))
        .group_by(Vote.region)
        .order_by(func.count(Vote.id).desc())
        .first()
    )
    top_station_row = (
        db.query(Vote.customs_station, func.count(Vote.id).label("cnt"))
        .group_by(Vote.customs_station)
        .order_by(func.count(Vote.id).desc())
        .first()
    )

    def gender_choice_pct(gender: str, choice: str) -> float:
        gender_total_local = db.query(func.count(Vote.id)).filter(Vote.gender == gender).scalar() or 0
        if gender_total_local == 0:
            return 0.0
        choice_count = (
            db.query(func.count(Vote.id))
            .filter(Vote.gender == gender, Vote.choice == choice)
            .scalar()
            or 0
        )
        return round((choice_count / gender_total_local) * 100, 1)

    region_rows = (
        db.query(Vote.region, func.count(Vote.id).label("cnt"))
        .group_by(Vote.region)
        .order_by(func.count(Vote.id).desc())
        .limit(5)
        .all()
    )
    station_rows = (
        db.query(Vote.customs_station, func.count(Vote.id).label("cnt"))
        .group_by(Vote.customs_station)
        .order_by(func.count(Vote.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total": total,
        "gender": {
            "male": male,
            "female": female,
            "male_pct": round((male / gender_total) * 100, 1),
            "female_pct": round((female / gender_total) * 100, 1),
        },
        "top_region": top_region_row[0] if top_region_row else "—",
        "top_region_count": top_region_row[1] if top_region_row else 0,
        "top_station": top_station_row[0] if top_station_row else "—",
        "top_station_count": top_station_row[1] if top_station_row else 0,
        "top_regions": [{"name": r[0], "count": r[1]} for r in region_rows],
        "top_stations": [{"name": r[0], "count": r[1]} for r in station_rows],
        "male_yes_pct": gender_choice_pct("Male", "yes"),
        "male_no_pct": gender_choice_pct("Male", "no"),
        "female_yes_pct": gender_choice_pct("Female", "yes"),
        "female_no_pct": gender_choice_pct("Female", "no"),
    }
