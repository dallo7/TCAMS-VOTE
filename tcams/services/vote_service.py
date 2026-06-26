from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from tcams.config import POLL_END_AT, POLL_START_AT, TARGET_NO_PCT, TARGET_NOT_SURE_PCT, TARGET_YES_PCT
from tcams.models import PollSession, Vote


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_countdown(seconds: int) -> str:
    days, rem = divmod(max(seconds, 0), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days} siku {hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


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


def sync_poll_schedule(db: Session) -> PollSession:
    poll = ensure_poll_session(db)
    now = utcnow()
    start = as_utc(POLL_START_AT)
    end = as_utc(POLL_END_AT)

    poll.started_at = start
    poll.ends_at = end

    if now < start:
        poll.status = "pending"
    elif now < end:
        poll.status = "active"
    else:
        poll.status = "closed"

    db.commit()
    db.refresh(poll)
    return poll


def start_poll(db: Session) -> PollSession:
    return sync_poll_schedule(db)


def get_active_poll(db: Session) -> PollSession | None:
    return sync_poll_schedule(db)


def is_poll_open(db: Session) -> bool:
    poll = get_active_poll(db)
    if poll is None:
        return False
    now = utcnow()
    start = as_utc(POLL_START_AT)
    end = as_utc(POLL_END_AT)
    return start <= now < end


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


def get_synthetic_tallies(db: Session) -> dict[str, int]:
    rows = (
        db.query(Vote.choice, func.count(Vote.id))
        .filter(Vote.is_synthetic.is_(True))
        .group_by(Vote.choice)
        .all()
    )
    counts = {"yes": 0, "no": 0, "not_sure": 0}
    for choice, count in rows:
        if choice in counts:
            counts[choice] = count
    return counts


def reset_votes(db: Session) -> int:
    deleted = db.query(Vote).delete()
    db.commit()
    sync_poll_schedule(db)
    return deleted


def get_time_remaining(db: Session) -> dict:
    poll = get_active_poll(db)
    if poll is None:
        return {"status": "pending", "seconds": 0, "label": "00:00:00", "phase": "pending"}

    now = utcnow()
    start = as_utc(POLL_START_AT)
    end = as_utc(POLL_END_AT)

    if now < start:
        seconds = max(int((start - now).total_seconds()), 0)
        return {
            "status": "pending",
            "seconds": seconds,
            "label": format_countdown(seconds),
            "phase": "until_start",
        }

    if now < end:
        seconds = max(int((end - now).total_seconds()), 0)
        return {
            "status": "active",
            "seconds": seconds,
            "label": format_countdown(seconds),
            "phase": "until_end",
        }

    return {"status": "closed", "seconds": 0, "label": "00:00:00", "phase": "closed"}
