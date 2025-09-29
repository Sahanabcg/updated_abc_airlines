from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Luggage
from app.schemas.luggage import LuggageCreate, LuggageUpdate


async def list_luggages(db: AsyncSession):
    result = await db.execute(select(Luggage))
    return result.scalars().all()


async def get_luggage(db: AsyncSession, luggage_id: int):
    result = await db.execute(select(Luggage).where(Luggage.id == luggage_id))
    return result.scalar_one_or_none()


async def create_luggage(db: AsyncSession, luggage_in: LuggageCreate):
    new_luggage = Luggage(**luggage_in.model_dump())
    db.add(new_luggage)
    try:
        await db.commit()
        await db.refresh(new_luggage)
        return new_luggage
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_luggage(db: AsyncSession, luggage_id: int, luggage_in: LuggageUpdate):
    luggage = await get_luggage(db, luggage_id)
    if not luggage:
        raise Exception("Luggage not found")
    for key, value in luggage_in.model_dump(exclude_unset=True).items():
        setattr(luggage, key, value)
    try:
        await db.commit()
        await db.refresh(luggage)
        return luggage
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def delete_luggage(db: AsyncSession, luggage_id: int):
    luggage = await get_luggage(db, luggage_id)
    if not luggage:
        raise Exception("Luggage not found")
    try:
        await db.delete(luggage)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
