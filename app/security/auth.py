import os, time
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.db.models import User

SECRET_KEY = os.getenv("JWT_SECRET", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", 3600))

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain, hashed):
    return pwd_ctx.verify(plain, hashed)


def hash_password(plain):
    return pwd_ctx.hash(plain)


async def get_user_by_email(db: AsyncSession, email: str):
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def authentic_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(sub: str, role: str, user_id: int):
    now = int(time.time())
    payload = {
        "sub": sub,
        "role": role,
        "uuid": user_id,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    db: AsyncSession = Depends(get_session), token: str = Depends(oauth2_schema)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("uuid")
        if not email or not user_id:
            raise ValueError("bad token")
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token",
        )
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
