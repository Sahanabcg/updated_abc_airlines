from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import TrackingEvent, Ticket, Luggage
from app.schemas.trackingevents import TrackingEventCreate, TrackingEventUpdate
from app.services.status_mapping import allowed_status


async def list_trackingevents(db: AsyncSession):
    result = await db.execute(select(TrackingEvent))
    return result.scalars().all()


async def get_tracking_event(db: AsyncSession, trackingevent_id: int):
    result = await db.execute(
        select(TrackingEvent).where(TrackingEvent.id == trackingevent_id)
    )
    return result.scalar_one_or_none()


async def create_tracking_event(
    db: AsyncSession, trackingevent_in: TrackingEventCreate
):
    new_tracking_event = TrackingEvent(**trackingevent_in.model_dump())
    db.add(new_tracking_event)
    try:
        await db.commit()
        await db.refresh(new_tracking_event)
        return new_tracking_event
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_tracking_event(
    db: AsyncSession, tracking_event_id: int, tracking_event_in: TrackingEventUpdate
):
    tracking_event = await get_tracking_event(db, tracking_event_id)
    if not tracking_event:
        raise Exception("Tracking event not found")
    for key, value in tracking_event_in.model_dump(exclude_unset=True).items():
        setattr(tracking_event, key, value)
        try:
            await db.commit()
            await db.refresh(tracking_event)
            return tracking_event
        except SQLAlchemyError as e:
            await db.rollback()
            raise e


async def delete_tracking_event(db: AsyncSession, tracking_event_id: int):
    tracking_event = await get_tracking_event(db, tracking_event_id)
    if not tracking_event:
        raise Exception("Tracking event not found")
    try:
        await db.delete(tracking_event)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise e




