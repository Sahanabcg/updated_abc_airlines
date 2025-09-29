from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, Luggage, Ticket, TrackingEvent


async def get_customer_by_tracking_event(db: AsyncSession, tracking_event_id: int):
    q = (
        select(User)
        .join(Ticket, User.id == Ticket.customer_id)
        .join(Luggage, Ticket.id == Luggage.ticket_id)
        .join(TrackingEvent, Luggage.id == TrackingEvent.luggage_id)
        .where(TrackingEvent.id == tracking_event_id)
        .limit(1)
    )
    customer = (await db.execute(q)).scalars().first()
    return customer
