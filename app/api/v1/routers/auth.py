from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_session
from app.db.models import User, UserRole
from app.security.auth import authentic_user, create_access_token, hash_password
from app.schemas.user import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    email=Form(...),
    password: str = Form(..., min_length=6),
    name: str = Form(None),
    phone: str = Form(None),
    address=Form(None),
    db: AsyncSession = Depends(get_session),
):
    exists = await db.scalar(select(User).where(User.email == email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.customer,
        name=name,
        phone=phone,
        address=address,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(sub=user.email, role=user.role.value, user_id=user.id)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/token", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)
):
    user = await authentic_user(db, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(sub=user.email, role=user.role.value, user_id=user.id)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)
