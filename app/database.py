from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

from .config import DATABASE_URL


# SQLite needs this option when used with FastAPI.
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# USER TABLE
# ---------------------------------------------------------

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(120)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column()

    goal: Mapped[str] = mapped_column(
        String(50)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------
# PLAN TABLE
# ---------------------------------------------------------

class Plan(Base):

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True
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
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------

def init_db():

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# USER FUNCTIONS
# ---------------------------------------------------------

def save_user(data: dict):

    with SessionLocal() as db:

        user = (
            db.query(User)
            .filter(User.user_id == data["user_id"])
            .first()
        )

        if user:

            for key, value in data.items():
                setattr(user, key, value)

        else:

            user = User(**data)

            db.add(user)

        db.commit()

        db.refresh(user)

        return user


def get_user(user_id: str):

    with SessionLocal() as db:

        return (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )


# ---------------------------------------------------------
# PLAN FUNCTIONS
# ---------------------------------------------------------

def save_plan(
    user_id: str,
    original_plan: str,
    nutrition_tip: str
):

    with SessionLocal() as db:

        plan = (
            db.query(Plan)
            .filter(Plan.user_id == user_id)
            .first()
        )

        if plan:

            plan.original_plan = original_plan
            plan.updated_plan = None
            plan.feedback = None
            plan.nutrition_tip = nutrition_tip
            plan.updated_at = None

        else:

            plan = Plan(
                user_id=user_id,
                original_plan=original_plan,
                nutrition_tip=nutrition_tip
            )

            db.add(plan)

        db.commit()

        db.refresh(plan)

        return plan


def get_plan(user_id: str):

    with SessionLocal() as db:

        return (
            db.query(Plan)
            .filter(Plan.user_id == user_id)
            .first()
        )


def update_plan(
    user_id: str,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str | None = None
):

    with SessionLocal() as db:

        plan = (
            db.query(Plan)
            .filter(Plan.user_id == user_id)
            .first()
        )

        if not plan:
            return None

        plan.updated_plan = updated_plan

        plan.feedback = feedback

        if nutrition_tip:
            plan.nutrition_tip = nutrition_tip

        plan.updated_at = datetime.now(timezone.utc)

        db.commit()

        db.refresh(plan)

        return plan


# ---------------------------------------------------------
# ADMIN FUNCTIONS
# ---------------------------------------------------------

def get_all_users():

    with SessionLocal() as db:

        return (
            db.query(User)
            .order_by(User.created_at.desc())
            .all()
        )


def get_all_plans():

    with SessionLocal() as db:

        return db.query(Plan).all()