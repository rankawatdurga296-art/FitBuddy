from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight_kg: Mapped[float] = mapped_column()

    goal: Mapped[str] = mapped_column(
        String(50)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    plan: Mapped["WorkoutPlan | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    user: Mapped[User] = relationship(
        back_populates="plan"
    )


if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }
else:
    connect_args = {}


engine = create_engine(
    settings.database_url,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def init_db() -> None:
    Base.metadata.create_all(
        bind=engine
    )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()