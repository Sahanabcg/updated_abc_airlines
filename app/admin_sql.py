from sqladmin import ModelView
from wtforms import SelectField, PasswordField
from markupsafe import Markup, escape
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.security.auth import hash_password

from app.db.models import (
    User,
    UserRole,
    Airport,
    Ticket,
    Luggage,
    TrackingEvent,
)


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.name, User.email, User.role, User.phone]
    column_searchable_list = [User.name, User.email, User.phone]
    form_columns = [
        User.name,
        User.email,
        User.phone,
        User.address,
        User.role,
       User.hashed_password
    ]
    column_labels = {"hashed_password": "Password"}

    form_overrides = {"role": SelectField, "hashed_password": PasswordField}
    form_args = {
        "role": {
            "choices": [(r.value, r.value.title()) for r in UserRole],
        },
        "hashed_password": {
            "label": "Password",
            "render_kw": {
                "placeholder": "Enter Password",
            },
        },
    }

    async def insert_model(self, request, data):
        password = data.pop("hashed_password", None)
        if password:
            data["hashed_password"] = hash_password(password)
        else:
            raise ValueError("Password is required")
        return await super().insert_model(request, data)

    async def update_model(self, request, pk, data):
        password = data.pop("hashed_password", None)
        if password:
            data["hashed_password"] = hash_password(password)
        return await super().update_model(request, pk, data)


class AirportAdmin(ModelView, model=Airport):
    name = "Airport"
    name_plural = "Airports"

    column_list = [
        Airport.id,
        Airport.code,
        Airport.city,
        Airport.state,
        Airport.country,
    ]
    column_searchable_list = [Airport.code, Airport.city, Airport.country]
    form_columns = [Airport.code, Airport.city, Airport.state, Airport.country]


class TicketAdmin(ModelView, model=Ticket):
    name = "Ticket"
    name_plural = "Tickets"

    column_list = [
        Ticket.id,
        Ticket.customer,
        Ticket.origin,
        Ticket.destination,
        Ticket.seat_class,
        Ticket.meal_included,
    ]
    column_searchable_list = [Ticket.origin, Ticket.destination]

    can_view_details = True
    column_details_list = [
        Ticket.id,
        Ticket.customer_id,
        Ticket.origin,
        Ticket.destination,
        Ticket.seat_class,
        Ticket.meal_included,
        Ticket.luggage_items,
    ]
    column_formatters_detail = {
        "luggage_items": lambda m, a: ", ".join(str(x) for x in (m.luggage_items or []))
        or "-"
    }

    form_columns = [
        "customer",
        "origin_airport",
        "destination_airport",
        "seat_class",
        "meal_included",
    ]

    form_overrides = {"meal_included": SelectField}
    form_args = {"meal_included": {"choices": [("yes", "Yes"), ("no", "No")]}}

    async def insert_model(self, request, data):
        async with AsyncSessionLocal() as s:
            oa = data.pop("origin_airport", None)
            da = data.pop("destination_airport", None)

            if hasattr(oa, "code"):
                data["origin"] = oa.code
            elif oa:
                data["origin"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(oa))
                )

            if hasattr(da, "code"):
                data["destination"] = da.code
            elif da:
                data["destination"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(da))
                )

        return await super().insert_model(request, data)

    async def update_model(self, request, pk, data):
        async with AsyncSessionLocal() as s:
            oa = data.pop("origin_airport", None)
            da = data.pop("destination_airport", None)

            if hasattr(oa, "code"):
                data["origin"] = oa.code
            elif oa:
                data["origin"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(oa))
                )

            if hasattr(da, "code"):
                data["destination"] = da.code
            elif da:
                data["destination"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(da))
                )

        return await super().update_model(request, pk, data)


class LuggageAdmin(ModelView, model=Luggage):
    name = "Luggage"
    name_plural = "Luggage"

    column_list = [
        Luggage.id,
        Luggage.ticket_id,
        Luggage.weight,
        Luggage.size,
        Luggage.status,
    ]
    column_searchable_list = [Luggage.ticket_id]
    can_view_details = True
    column_details_list = [
        Luggage.id,
        Luggage.ticket,
        Luggage.weight,
        Luggage.size,
        Luggage.status,
        Luggage.tracking_events,
    ]
    column_formatters_detail = {
        "tracking_events": lambda m, a: (
            ", ".join(str(x.id) for x in (m.tracking_events or [])) or "-"
        )
    }
    form_columns = ["ticket", "weight", "size", "status"]


class TrackingEventAdmin(ModelView, model=TrackingEvent):
    name = "Tracking Event"
    name_plural = "Tracking Events"

    column_list = [
        TrackingEvent.id,
        TrackingEvent.luggage_id,
        TrackingEvent.status,
        TrackingEvent.last_location,
        TrackingEvent.scan_datetime,
        TrackingEvent.next_destination,
    ]
    column_searchable_list = [
        TrackingEvent.luggage_id,
        TrackingEvent.last_location,
        TrackingEvent.next_destination,
    ]
    can_view_details = True
    column_details_list = [
        TrackingEvent.id,
        TrackingEvent.luggage,
        TrackingEvent.status,
        TrackingEvent.last_location,
        TrackingEvent.scan_datetime,
        TrackingEvent.next_destination,
    ]
    column_formatters_detail = {
        "luggage": lambda m, a: str(m.luggage) if getattr(m, "luggage", None) else "-"
    }
    form_columns = [
        "luggage",
        "status",
        "last_location_airport",
        "scan_datetime",
        "next_destination_airport",
    ]

    async def insert_model(self, request, data):
        async with AsyncSessionLocal() as s:
            lla = data.pop("last_location_airport", None)
            nd = data.pop("next_destination_airport", None)

            if hasattr(lla, "code"):
                data["last_location"] = lla.code
            elif lla:
                data["last_location"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(lla))
                )

            if hasattr(nd, "code"):
                data["next_destination"] = nd.code
            elif nd:
                data["next_destination"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(nd))
                )

        return await super().insert_model(request, data)

    async def update_model(self, request, pk, data):
        async with AsyncSessionLocal() as s:
            lla = data.pop("last_location_airport", None)
            nd = data.pop("next_destination_airport", None)

            if hasattr(lla, "code"):
                data["last_location"] = lla.code
            elif lla:
                data["last_location"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(lla))
                )

            if hasattr(nd, "code"):
                data["next_destination"] = nd.code
            elif nd:
                data["next_destination"] = await s.scalar(
                    select(Airport.code).where(Airport.id == int(nd))
                )

        return await super().update_model(request, pk, data)
