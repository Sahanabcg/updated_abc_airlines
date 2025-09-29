from sqlalchemy.orm import declarative_base, relationship, mapped_column, Mapped
from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum as SAEnum
from typing import List, Optional
from enum import Enum
from app.db.enum import TrackingStatus

Base = declarative_base()


class UserRole(str, Enum):
    admin = "admin"
    customer = "customer"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.customer, nullable=False
    )

    name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(String(255))

    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name or self.email or str(self.id)


class Airport(Base):
    __tablename__ = "airport"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(10), unique=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    def __str__(self) -> str:
        code = self.code or "-"
        loc = ", ".join(p for p in [self.city, self.state, self.country] if p)
        return f"{code} – {loc}" if loc else code


class Ticket(Base):
    __tablename__ = "ticket"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))

    origin: Mapped[Optional[str]] = mapped_column(ForeignKey("airport.code"))
    destination: Mapped[Optional[str]] = mapped_column(ForeignKey("airport.code"))
    seat_class: Mapped[Optional[str]] = mapped_column("class", String(50))
    meal_included: Mapped[Optional[str]] = mapped_column(String(50))

    customer: Mapped[Optional["User"]] = relationship(back_populates="tickets")

    origin_airport: Mapped[Optional["Airport"]] = relationship(
        foreign_keys=[origin], primaryjoin="Ticket.origin==Airport.code"
    )
    destination_airport: Mapped[Optional["Airport"]] = relationship(
        foreign_keys=[destination], primaryjoin="Ticket.destination==Airport.code"
    )

    luggage_items: Mapped[List["Luggage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return f"Ticket #{self.id} {self.origin or '?'}→{self.destination or '?'}"


class Luggage(Base):
    __tablename__ = "luggage"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ticket.id"))
    weight: Mapped[Optional[int]] = mapped_column(Integer)
    size: Mapped[Optional[str]] = mapped_column(String(50))
    ticket: Mapped[Optional["Ticket"]] = relationship(back_populates="luggage_items")
    tracking_events: Mapped[List["TrackingEvent"]] = relationship(
        back_populates="luggage", cascade="all, delete-orphan"
    )
    status: Mapped[TrackingStatus] = mapped_column(
        SAEnum(TrackingStatus, name="tracking_status"),
        index=True,
        nullable=False,
        default=TrackingStatus.NEW,
        server_default=TrackingStatus.NEW.value,
    )

    def __str__(self) -> str:
        return str(self.id)


class TrackingEvent(Base):
    __tablename__ = "tracking_event"
    id: Mapped[int] = mapped_column(primary_key=True)
    luggage_id: Mapped[int] = mapped_column(
        ForeignKey("luggage.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[TrackingStatus] = mapped_column(
        SAEnum(TrackingStatus, name="tracking_status_enum"), index=True, nullable=False
    )
    last_location: Mapped[Optional[str]] = mapped_column(ForeignKey("airport.code"))
    scan_datetime: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    next_destination: Mapped[Optional[str]] = mapped_column(ForeignKey("airport.code"))
    luggage: Mapped["Luggage"] = relationship(back_populates="tracking_events")
    last_location_airport: Mapped[Optional["Airport"]] = relationship(
        foreign_keys=[last_location], primaryjoin="TrackingEvent.last_location==Airport.code"
    )
    next_destination_airport: Mapped[Optional["Airport"]] = relationship(
        foreign_keys=[next_destination], primaryjoin="TrackingEvent.next_destination==Airport.code"
    )

