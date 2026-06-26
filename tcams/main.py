import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from starlette.middleware.wsgi import WSGIMiddleware

from tcams.config import ADMIN_TOKEN, APP_VERSION
from tcams.database import Base, SessionLocal, engine, get_db
from tcams.dash_app.app import create_dash_app
from tcams.dash_app.callbacks import register_callbacks
from tcams.models import Agent
from tcams.seed import seed_agents
from tcams.services.steering_engine import start_steering_scheduler, stop_steering_scheduler
from tcams.services.vote_service import (
    ensure_poll_session,
    get_tallies,
    get_time_remaining,
    is_poll_open,
    record_vote,
    reset_votes,
    start_poll,
    sync_poll_schedule,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
_bootstrap = SessionLocal()
try:
    agent_count = seed_agents(_bootstrap)
    sync_poll_schedule(_bootstrap)
    poll = ensure_poll_session(_bootstrap)
    logger.info("Poll schedule synced: status=%s", poll.status)
    logger.info("Agents in database: %s", agent_count)
finally:
    _bootstrap.close()

dash_app = create_dash_app(SessionLocal)
register_callbacks(dash_app)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_steering_scheduler()
    logger.info("TCAMS polling app ready")
    yield
    stop_steering_scheduler()


app = FastAPI(title="TCAMS Polling API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "tcams-polling", "version": APP_VERSION}


@app.get("/api/tallies")
def api_tallies(db=Depends(get_db)):
    return {
        "tallies": get_tallies(db),
        "time": get_time_remaining(db),
        "open": is_poll_open(db),
    }


class VotePayload(BaseModel):
    choice: str
    voter_name: str
    gender: str
    region: str
    customs_station: str
    reason: str | None = None


@app.post("/api/votes")
def api_vote(payload: VotePayload, db=Depends(get_db)):
    if not is_poll_open(db):
        raise HTTPException(status_code=400, detail="Poll is closed")
    if payload.choice not in {"yes", "no", "not_sure"}:
        raise HTTPException(status_code=400, detail="Invalid choice")
    vote = record_vote(
        db,
        choice=payload.choice,
        voter_name=payload.voter_name,
        gender=payload.gender,
        region=payload.region,
        customs_station=payload.customs_station,
        reason=payload.reason,
    )
    return {"id": vote.id, "choice": vote.choice}


@app.post("/api/poll/start")
def api_poll_start(x_admin_token: str | None = Header(default=None), db=Depends(get_db)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    poll = start_poll(db)
    return {
        "status": poll.status,
        "started_at": poll.started_at.isoformat() if poll.started_at else None,
        "ends_at": poll.ends_at.isoformat() if poll.ends_at else None,
    }


@app.post("/api/poll/reset-votes")
def api_reset_votes(x_admin_token: str | None = Header(default=None), db=Depends(get_db)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    deleted = reset_votes(db)
    return {"deleted": deleted, "tallies": get_tallies(db), "time": get_time_remaining(db)}


@app.get("/api/regions")
def api_regions(db=Depends(get_db)):
    regions = db.query(Agent.region).distinct().order_by(Agent.region).all()
    return [r[0] for r in regions]


app.mount("/", WSGIMiddleware(dash_app.server))
