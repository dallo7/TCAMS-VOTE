from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tcams.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sn: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    region: Mapped[str] = mapped_column(String(128), nullable=False)
    customs_station: Mapped[str] = mapped_column(String(255), nullable=False)
    used_for_steering: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    choice: Mapped[str] = mapped_column(String(16), nullable=False)
    voter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    region: Mapped[str] = mapped_column(String(128), nullable=False)
    customs_station: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="public", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class PollSession(Base):
    __tablename__ = "poll_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_yes_pct: Mapped[float] = mapped_column(Float, default=52.4, nullable=False)
    target_no_pct: Mapped[float] = mapped_column(Float, default=31.4, nullable=False)
    target_not_sure_pct: Mapped[float] = mapped_column(Float, default=16.2, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
