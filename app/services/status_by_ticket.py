from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.models import TrackingEvent, Ticket, Luggage


async def get_status_by_ticket(db: AsyncSession, ticket_id: int):
    base = (
        select(
            TrackingEvent.id.label("te_id"),
            func.row_number().over(
                partition_by=TrackingEvent.luggage_id,
                order_by=TrackingEvent.scan_datetime.desc().nullslast(),
            ).label("rn"),
        )
        .join(Luggage, TrackingEvent.luggage_id == Luggage.id)
        .where(Luggage.ticket_id == ticket_id)
        .subquery()
    )
    q = select(TrackingEvent).join(base, TrackingEvent.id == base.c.te_id).where(base.c.rn == 1)
    rows = await db.scalars(q)
    return list(rows)
