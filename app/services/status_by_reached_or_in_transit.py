from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.models import TrackingEvent
from app.services.status_mapping import allowed_status


async def get_status_by_tracking_status(db: AsyncSession, status: str):
    target_status = allowed_status(status)
    latest_event = (
        select(TrackingEvent.luggage_id, func.max(TrackingEvent.id).label("last_id"))
        .group_by(TrackingEvent.luggage_id)
        .subquery()
    )
    q = (
        select(TrackingEvent)
        .join(latest_event, (TrackingEvent.id == latest_event.c.last_id))
        .where(TrackingEvent.status.in_(target_status))
        .order_by(TrackingEvent.luggage_id)
    )
    result = await db.execute(q)
    return result.scalars().all()
