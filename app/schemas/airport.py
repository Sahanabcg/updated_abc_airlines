from typing import Optional
from pydantic import BaseModel,field_validator
from .common import ORMBaseModel


class AirportBase(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    code : Optional[str] = None

    @field_validator('code',mode='before')
    @classmethod
    def to_upper(cls, v):
        if v:
            return v.upper().strip()
        return v


class AirportCreate(AirportBase):
    code: str


class AirportUpdate(AirportBase):
    pass


class AirportRead(ORMBaseModel, AirportBase):
    code: str
