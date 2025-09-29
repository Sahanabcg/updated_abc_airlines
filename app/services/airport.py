from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.models import Airport
from app.schemas.airport import AirportCreate, AirportUpdate


async def list_airports(db: AsyncSession):
    result = await db.execute(select(Airport))
    return result.scalars().all()


async def get_airport(db: AsyncSession, code: str):
    result = await db.execute(select(Airport).where(Airport.code == code))
    return result.scalar_one_or_none()


async def create_airport(db: AsyncSession, airport_in: AirportCreate):
    new_airport = Airport(**airport_in.model_dump())
    db.add(new_airport)
    try:
        await db.commit()
        await db.refresh(new_airport)
        return new_airport
    except IntegrityError as e:
        await db.rollback()
        raise Exception("Airport with this code already exists") from e
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_airport(db: AsyncSession, code: str, airport_in: AirportUpdate):
    airport = await get_airport(db, code)
    if not airport:
        raise Exception("Airport not found")
    for key, value in airport_in.model_dump(exclude_unset=True).items():
        setattr(airport, key, value)
    try:
        await db.commit()
        await db.refresh(airport)
        return airport
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def delete_airport(db: AsyncSession, code: str):
    airport = await get_airport(db, code)
    if not airport:
        raise Exception("Airport not found")
    try:
        await db.delete(airport)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
