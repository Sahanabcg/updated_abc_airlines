from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routers import (
    airport,
    customer,
    ticket,
    luggage,
    trackingevents,
    main_api,
    auth,
)
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.authentication import AuthCredentials, SimpleUser
from sqlalchemy import select
from app.db.database import engine, AsyncSessionLocal
from app.db.models import User
from app.security.auth import verify_password

app = FastAPI(title=settings.app_name)

app.include_router(airport.router, prefix="/api/v1")
app.include_router(customer.router, prefix="/api/v1")
app.include_router(ticket.router, prefix="/api/v1")
app.include_router(luggage.router, prefix="/api/v1")
app.include_router(trackingevents.router, prefix="/api/v1")
app.include_router(main_api.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key):
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request):
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        if not email or not password:
            return False

        async with AsyncSessionLocal() as session:
            res = await session.execute(select(User).where(User.email == email))
            user = res.scalar_one_or_none()

            role_val = (
                getattr(user.role, "value", getattr(user, "role", None))
                if user
                else None
            )
            if (
                user
                and role_val == "admin"
                and verify_password(password, user.hashed_password)
            ):
                request.session.update({"user": email})
                return True
            return False

    async def logout(self, request: Request):
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        user = request.session.get("user")
        if user:
            return AuthCredentials(["authenticated"]), SimpleUser(user)
        return None


admin = Admin(
    app,
    engine,
    authentication_backend=AdminAuth(secret_key=settings.admin_session_secret),
)

from app.admin_sql import (
    UserAdmin,
    AirportAdmin,
    TicketAdmin,
    LuggageAdmin,
    TrackingEventAdmin,
)

admin.add_view(UserAdmin)
admin.add_view(AirportAdmin)
admin.add_view(TicketAdmin)
admin.add_view(LuggageAdmin)
admin.add_view(TrackingEventAdmin)
