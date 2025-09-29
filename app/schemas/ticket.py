from typing import Optional, Literal
from .common import ORMBaseModel

meal_type = Literal["Yes", "No"]


class TicketBase(ORMBaseModel):
    customer_id: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    seat_class: Optional[str] = None
    meal_included: Optional[meal_type] = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(TicketBase):
    pass


class TicketRead(TicketBase):
    id: int
