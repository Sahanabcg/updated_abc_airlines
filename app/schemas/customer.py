from typing import Optional
from pydantic import EmailStr, constr
from .common import ORMBaseModel

PhoneStr = constr(strip_whitespace=True, min_length=7, max_length=15)


class CustomerBase(ORMBaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
