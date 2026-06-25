import logging
import random
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func
from sqlalchemy.orm import Session

from tcams.config import (
    FINAL_PHASE_HOURS,
    GAP_TARGETS_PP,
    INTERVALS_MIN,
    MAX_GAP_STEADY,
    MAX_GAP_TRIGGER,
    STEERING_TICK_SECONDS,
    TARGET_NO_PCT,
    TARGET_NOT_SURE_PCT,
    TARGET_YES_PCT,
)
from tcams.database import SessionLocal
from tcams.models import Agent
from tcams.services.name_generator import generate_swahili_name
from tcams.services.vote_service import get_active_poll, get_tallies, record_vote, utcnow, as_utc

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _jitter_minutes(base_min: float) -> float:
    factor = random.uniform(0.85, 1.3)
    return max(base_min * factor, 0.5)


def _compute_gap_pp(tallies: dict) -> float:
    pct = tallies["percentages"]
    return pct["no"] - pct["yes"]


def _pick_unused_agent(db: Session) -> Agent | None:
    return (
        db.query(Agent)
        .filter(Agent.used_for_steering.is_(False))
        .order_by(func.random())
        .first()
    )


def _inject_vote(db: Session, choice: str, source: str = "steering") -> bool:
    agent = _pick_unused_agent(db)
    if agent:
        record_vote(
            db,
            choice=choice,
            voter_name=agent.name,
            gender=agent.gender,
            region=agent.region,
            customs_station=agent.customs_station,
            reason=None,
            is_synthetic=True,
            source=source,
        )
        agent.used_for_steering = True
        db.commit()
        return True

    name, gender = generate_swahili_name()
    regions = db.query(Agent.region).distinct().all()
    stations = db.query(Agent.customs_station).distinct().all()
    region = random.choice(regions)[0] if regions else "Dar es Salaam"
    station = random.choice(stations)[0] if stations else "Dar es Salaam Port (TICTS)"
    record_vote(
        db,
        choice=choice,
        voter_name=name,
        gender=gender,
        region=region,
        customs_station=station,
        reason=None,
        is_synthetic=True,
        source="auto_generated",
    )
    return True


def _votes_needed_for_targets(tallies: dict) -> dict:
    counts = tallies["counts"]
    y, n, s = counts["yes"], counts["no"], counts["not_sure"]
    total = tallies["total"]

    if total == 0:
        return {"yes": 3, "no": 2, "not_sure": 1}

    target_y = TARGET_YES_PCT / 100
    target_n = TARGET_NO_PCT / 100
    target_s = TARGET_NOT_SURE_PCT / 100

    best = {"yes": 0, "no": 0, "not_sure": 0, "score": float("inf")}
    max_add = max(50, int(total * 0.05) + 5)

    for add in range(1, max_add + 1):
        for dy in range(add + 1):
            for dn in range(add + 1 - dy):
                ds = add - dy - dn
                new_total = total + add
                py = (y + dy) / new_total * 100
                pn = (n + dn) / new_total * 100
                ps = (s + ds) / new_total * 100
                score = (
                    abs(py - TARGET_YES_PCT)
                    + abs(pn - TARGET_NO_PCT)
                    + abs(ps - TARGET_NOT_SURE_PCT)
                )
                if score < best["score"]:
                    best = {"yes": dy, "no": dn, "not_sure": ds, "score": score}

    return {"yes": best["yes"], "no": best["no"], "not_sure": best["not_sure"]}


def steering_tick() -> None:
    if random.random() < 0.12:
        return

    db = SessionLocal()
    try:
        poll = get_active_poll(db)
        if poll is None or poll.status != "active" or poll.ends_at is None:
            return

        tallies = get_tallies(db)
        gap = _compute_gap_pp(tallies)
        remaining = as_utc(poll.ends_at) - utcnow()
        hours_left = remaining.total_seconds() / 3600

        if hours_left <= 0:
            poll.status = "closed"
            db.commit()
            return

        if hours_left <= FINAL_PHASE_HOURS:
            needed = _votes_needed_for_targets(tallies)
            batch_size = min(needed["yes"] + needed["not_sure"], random.randint(1, 4))
            for _ in range(batch_size):
                if needed["yes"] > 0:
                    _inject_vote(db, "yes")
                    needed["yes"] -= 1
                elif needed["not_sure"] > 0:
                    _inject_vote(db, "not_sure")
                    needed["not_sure"] -= 1
                else:
                    break
            return

        if gap > MAX_GAP_TRIGGER:
            interval = random.choice(INTERVALS_MIN)
            delay = _jitter_minutes(interval)
            schedule_injection("yes", delay)
            return

        target_gap = random.choice(GAP_TARGETS_PP)
        if gap > target_gap:
            interval = random.choice(INTERVALS_MIN)
            delay = _jitter_minutes(interval * 1.5)
            schedule_injection("yes", delay)
            return

        if gap > MAX_GAP_STEADY and random.random() < 0.35:
            delay = _jitter_minutes(random.choice(INTERVALS_MIN) * 2)
            schedule_injection("yes", delay)

        pct = tallies["percentages"]
        if pct["not_sure"] < TARGET_NOT_SURE_PCT - 3 and random.random() < 0.15:
            delay = _jitter_minutes(random.choice(INTERVALS_MIN) * 3)
            schedule_injection("not_sure", delay)

    except Exception:
        logger.exception("Steering tick failed")
    finally:
        db.close()


def inject_vote_job(choice: str) -> None:
    db = SessionLocal()
    try:
        poll = get_active_poll(db)
        if poll is None or poll.status != "active":
            return
        _inject_vote(db, choice)
    except Exception:
        logger.exception("Injection job failed")
    finally:
        db.close()


def schedule_injection(choice: str, delay_minutes: float) -> None:
    global _scheduler
    if _scheduler is None:
        return
    run_date = utcnow() + timedelta(minutes=delay_minutes)
    _scheduler.add_job(
        inject_vote_job,
        trigger="date",
        run_date=run_date.replace(tzinfo=None),
        args=[choice],
        id=f"inject-{choice}-{run_date.timestamp()}",
        replace_existing=False,
        max_instances=3,
    )


def start_steering_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        steering_tick,
        trigger="interval",
        seconds=STEERING_TICK_SECONDS,
        id="steering-tick",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Steering scheduler started")
    return _scheduler


def stop_steering_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
