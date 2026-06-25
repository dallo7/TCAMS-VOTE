from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from tcams.config import POLL_DURATION_HOURS, TARGET_NO_PCT, TARGET_NOT_SURE_PCT, TARGET_YES_PCT
from tcams.models import PollSession, Vote


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def ensure_poll_session(db: Session) -> PollSession:
    poll = db.query(PollSession).first()
    if poll is None:
        poll = PollSession(
            target_yes_pct=TARGET_YES_PCT,
            target_no_pct=TARGET_NO_PCT,
            target_not_sure_pct=TARGET_NOT_SURE_PCT,
            status="pending",
        )
        db.add(poll)
        db.commit()
        db.refresh(poll)
    return poll


def start_poll(db: Session) -> PollSession:
    poll = ensure_poll_session(db)
    now = utcnow()
    poll.started_at = now
    poll.ends_at = now + timedelta(hours=POLL_DURATION_HOURS)
    poll.status = "active"
    db.commit()
    db.refresh(poll)
    return poll


def get_active_poll(db: Session) -> PollSession | None:
    poll = db.query(PollSession).first()
    if poll is None:
        return None
    if poll.status == "active" and poll.ends_at and utcnow() >= as_utc(poll.ends_at):
        poll.status = "closed"
        db.commit()
    return poll


def is_poll_open(db: Session) -> bool:
    poll = get_active_poll(db)
    return poll is not None and poll.status == "active" and poll.ends_at and utcnow() < as_utc(poll.ends_at)


def record_vote(
    db: Session,
    *,
    choice: str,
    voter_name: str,
    gender: str,
    region: str,
    customs_station: str,
    reason: str | None = None,
    is_synthetic: bool = False,
    source: str = "public",
) -> Vote:
    vote = Vote(
        choice=choice,
        voter_name=voter_name,
        gender=gender,
        region=region,
        customs_station=customs_station,
        reason=reason,
        is_synthetic=is_synthetic,
        source=source,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


def get_tallies(db: Session) -> dict:
    rows = db.query(Vote.choice, func.count(Vote.id)).group_by(Vote.choice).all()
    counts = {"yes": 0, "no": 0, "not_sure": 0}
    for choice, count in rows:
        if choice in counts:
            counts[choice] = count
    total = sum(counts.values())
    percentages = {
        key: round((value / total) * 100, 1) if total else 0.0
        for key, value in counts.items()
    }
    return {"counts": counts, "total": total, "percentages": percentages}


def get_time_remaining(db: Session) -> dict:
    poll = get_active_poll(db)
    if poll is None or poll.ends_at is None:
        return {"status": poll.status if poll else "pending", "seconds": 0, "label": "00:00:00"}

    remaining = as_utc(poll.ends_at) - utcnow()
    seconds = max(int(remaining.total_seconds()), 0)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return {
        "status": poll.status,
        "seconds": seconds,
        "label": f"{hours:02d}:{minutes:02d}:{secs:02d}",
    }
