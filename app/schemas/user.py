from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from app.db.models import UserRole

Role = Literal["admin", "customer"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None



class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    user_id: int
