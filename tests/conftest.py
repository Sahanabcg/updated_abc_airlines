import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.db.models import Base, User, UserRole, Airport, Ticket, Luggage, TrackingEvent
from app.security.auth import hash_password, get_current_user
from app.db.database import get_session
from app.main import app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest_asyncio.fixture()
async def session(engine) -> AsyncSession:
    Session = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    async with Session() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture(autouse=True)
async def _override_db(session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture()
async def seed_data(session: AsyncSession):
    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.admin,
    )
    a = User(
        email="a@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.customer,
        name="A",
    )
    b = User(
        email="b@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.customer,
        name="B",
    )

    jfk = Airport(code="JFK", city="NY", country="US")
    sfo = Airport(code="SFO", city="SF", country="US")

    t_a = Ticket(
        customer_id=2,
        origin="JFK",
        destination="SFO",
        seat_class="E",
        meal_included="yes",
    )
    t_b = Ticket(
        customer_id=3,
        origin="SFO",
        destination="JFK",
        seat_class="E",
        meal_included="no",
    )

    l1 = Luggage(ticket=t_a, weight=10, size="S")
    l2 = Luggage(ticket=t_a, weight=12, size="M")
    l3 = Luggage(ticket=t_b, weight=9, size="S")

    ev1 = TrackingEvent(
        luggage=l1, status="IN_TRANSIT", last_location="JFK", next_destination="SFO"
    )
    ev2 = TrackingEvent(
        luggage=l2, status="APPROVED", last_location="SFO", next_destination="SFO"
    )
    ev3 = TrackingEvent(
        luggage=l3, status="IN_TRANSIT", last_location="SFO", next_destination="JFK"
    )

    session.add_all([admin, a, b, jfk, sfo, t_a, t_b, l1, l2, l3, ev1, ev2, ev3])
    await session.commit()
    return {
        "admin": admin,
        "a": a,
        "b": b,
        "t_a": t_a,
        "t_b": t_b,
        "ev1": ev1,
        "ev2": ev2,
        "ev3": ev3,
    }


@pytest.fixture()
def as_admin(seed_data):
    app.dependency_overrides[get_current_user] = lambda: seed_data["admin"]
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def as_a(seed_data):
    app.dependency_overrides[get_current_user] = lambda: seed_data["a"]
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def as_b(seed_data):
    app.dependency_overrides[get_current_user] = lambda: seed_data["b"]
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
