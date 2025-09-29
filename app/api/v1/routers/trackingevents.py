from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.trackingevents import (
    TrackingEventCreate,
    TrackingEventRead,
    TrackingEventUpdate,
)
from app.services import trackingevents as trackingevent_service


router = APIRouter(prefix="/trackingevent", tags=["trackingevent"])


@router.post("/", response_model=TrackingEventRead)
async def create_tracking_event(
    tracking_event: TrackingEventCreate, db: AsyncSession = Depends(get_session)
):
    try:
        return await trackingevent_service.create_tracking_event(db, tracking_event)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not create tracking event: {str(e)}"
        )


@router.get("/", response_model=list[TrackingEventRead])
async def list_tracking_events(db: AsyncSession = Depends(get_session)):
    return await trackingevent_service.list_trackingevents(db)


@router.get("/{trackingevent_id}", response_model=TrackingEventRead)
async def get_tracking_event(
    trackingevent_id: int, db: AsyncSession = Depends(get_session)
):
    tracking_event = await trackingevent_service.get_tracking_event(
        db, trackingevent_id
    )
    if not tracking_event:
        raise HTTPException(status_code=404, detail="Tracking event not found")
    return tracking_event


@router.patch("/{trackingevent_id}", response_model=TrackingEventRead)
async def update_tracking_event(
    trackingevent_id: int,
    tracking_event: TrackingEventUpdate,
    db: AsyncSession = Depends(get_session),
):
    tracking_event = await trackingevent_service.update_tracking_event(
        db, trackingevent_id, tracking_event
    )
    if not tracking_event:
        raise HTTPException(status_code=404, detail="Tracking event not found")
    return tracking_event


@router.delete("/{trackingevent_id}", status_code=status.HTTP_200_OK)
async def delete_tracking_event(
    trackingevent_id: int, db: AsyncSession = Depends(get_session)
):
    success = await trackingevent_service.delete_tracking_event(db, trackingevent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tracking event not found")
    return {"deleted": True, "trackingevent_id": trackingevent_id}


