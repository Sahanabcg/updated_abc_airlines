from typing import Optional
from .common import ORMBaseModel


class LuggageBase(ORMBaseModel):
    ticket_id: Optional[int] = None
    weight: Optional[int] = None
    size: Optional[str] = None


class LuggageCreate(LuggageBase):
    ticket_id: int


class LuggageUpdate(LuggageBase):
    pass


class LuggageRead(LuggageBase):
    id: int
