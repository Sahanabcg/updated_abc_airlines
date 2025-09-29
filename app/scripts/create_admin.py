import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User, UserRole
from app.security.auth import hash_password
from app.core.config import settings

async def main():
    async with AsyncSessionLocal() as session:
        email = settings.admin_email
        password = settings.admin_password.get_secret_value()
        if not email or not password:
            raise RuntimeError("Missing ADMIN_EMAIL or ADMIN_PASSWORD in .env")

        existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

        if existing:
            existing.role = UserRole.admin
            existing.hashed_password = hash_password(password)
            print(f"Updated existing user {email} -> admin")
        else:
            session.add(User(
                email=email,
                hashed_password=hash_password(password),
                role=UserRole.admin,
            ))
            print(f"Created admin user {email}")

        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
