from typing import Optional
from .common import ORMBaseModel
from datetime import datetime
from app.db.enum import TrackingStatus



class TrackingEventBase(ORMBaseModel):
    last_location: Optional[str] = None
    scan_datetime: Optional[datetime] = None
    next_destination: Optional[str] = None
    status: Optional[TrackingStatus] = None


class TrackingEventCreate(TrackingEventBase):
    status: TrackingStatus
    luggage_id: int


class TrackingEventUpdate(TrackingEventBase):
    status: Optional[TrackingStatus] = None


class TrackingEventRead(TrackingEventBase):
    id: int
    status: TrackingStatus
    luggage_id: int
