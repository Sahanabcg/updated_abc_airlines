from app.services import luggage_reached
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services import (
    luggage_reached,
    status_by_reached_or_in_transit,
    status_by_ticket,
    customer_lookup,
)
from app.schemas.trackingevents import (
    TrackingEventRead,
)
from app.schemas.user import UserRead
from app.db.models import User, UserRole, Ticket
from sqlalchemy import select
from app.security.auth import get_current_user
from app.security.permissions import (
    verify_owner_or_admin,
    verify_owner_by_ticket_id,
    verify_owner_by_tracking_id,
)


router = APIRouter(prefix="/main_api", tags=["main_api"])


@router.get("/status_by_ticket/{ticket_id}", response_model=list[TrackingEventRead])
async def get_status_by_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    exists = await db.scalar(select(Ticket.id).where(Ticket.id == ticket_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await verify_owner_by_ticket_id(db, user, ticket_id)
    return await status_by_ticket.get_status_by_ticket(db, ticket_id)


@router.get("/status_by_luggage/{status}", response_model=list[TrackingEventRead])
async def get_status_by_luggage(
    status: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only")
    try:
        return await status_by_reached_or_in_transit.get_status_by_tracking_status(
            db, status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch status: {str(e)}")


@router.get("/luggages/reached/{customer_id}")
async def get_reached_luggages(
    customer_id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    await verify_owner_or_admin(user, customer_id)
    try:
        result = await luggage_reached.all_luggage_reached(db, customer_id)
        if result["summary"]["total_luggage"] == 0:
            raise HTTPException(
                status_code=404, detail="No reached luggages found for this customer"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not fetch reached luggages: {str(e)}"
        )


@router.get("/customer_lookup/{tracking_event_id}", response_model=UserRead)
async def customer_lookup_by_tracking_event(
    tracking_event_id: int,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    await verify_owner_by_tracking_id(db, user, tracking_event_id)
    try:
        result = await customer_lookup.get_customer_by_tracking_event(
            db, tracking_event_id
        )
        if not result:
            raise HTTPException(
                status_code=404, detail="No customer found for this tracking event"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not fetch customer: {str(e)}"
        )
