from app.db.models import User, TrackingEvent, Ticket, Luggage
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def all_luggage_reached(db: AsyncSession, customer_id: int):
    last_event = (
        select(TrackingEvent.luggage_id, func.max(TrackingEvent.id).label("last_id"))
        .group_by(TrackingEvent.luggage_id)
        .subquery()
    )
    q = (
        select(
            Luggage.id.label("luggage_id"),
            TrackingEvent.status.label("status"),
            TrackingEvent.last_location,
            TrackingEvent.scan_datetime,
        )
        .join(Ticket, Ticket.id == Luggage.ticket_id)
        .where(Ticket.customer_id == customer_id)
        .join(last_event, last_event.c.luggage_id == Luggage.id)
        .join(TrackingEvent, TrackingEvent.id == last_event.c.last_id)
        .order_by(Luggage.id)
    )
    result = (await db.execute(q)).all()
    total_luggage = len(result)
    reached_count = sum(1 for row in result if (row.status).upper() == "APPROVED")
    return {
        "customer_id": customer_id,
        "all_reached": total_luggage > 0 and total_luggage == reached_count,
        "summary": {
            "total_luggage": total_luggage,
            "reached": reached_count,
            "in_transit": total_luggage - reached_count,
        },
        "details": [
            {
                "luggage_id": row.luggage_id,
                "status": row.status,
                "last_location": row.last_location,
                "scan_datetime": row.scan_datetime,
            }
            for row in result
        ],
    }
