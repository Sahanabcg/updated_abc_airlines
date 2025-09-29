from fastapi import HTTPException, status
from sqlalchemy import select
from app.db.models import User, UserRole, Ticket, Luggage, TrackingEvent
from sqlalchemy.ext.asyncio import AsyncSession


async def verify_owner_or_admin(current: User, owner_id: int):
    print("owner",owner_id)
    if current.role == UserRole.admin or current.id == owner_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


async def verify_owner_by_ticket_id(
    db: AsyncSession, current_user: User, ticket_id: int
):
    owner_id = await db.scalar(select(Ticket.customer_id).where(Ticket.id == ticket_id))
    if owner_id is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role!=UserRole.admin and current_user.id!=owner_id:
        raise HTTPException(status_code=403,detail="Forbidden")
    await verify_owner_or_admin(current_user, owner_id)


async def verify_owner_by_tracking_id(
    db: AsyncSession, current_user: User, event_id: int
):
    owner_id = await db.scalar(
        select(Ticket.customer_id)
        .join(Luggage, Luggage.ticket_id == Ticket.id)
        .join(TrackingEvent, TrackingEvent.luggage_id == Luggage.id)
        .where(TrackingEvent.id == event_id)
    )
    if owner_id is None:
        raise HTTPException(status_code=404, detail="Tracking event not found")
    if current_user.role!=UserRole.admin and current_user.id!=owner_id:
        raise HTTPException(status_code=404,detail="Not found")
    await verify_owner_or_admin(current_user, owner_id)
