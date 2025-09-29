from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


async def list_tickets(db: AsyncSession):
    result = await db.execute(select(Ticket))
    return result.scalars().all()


async def get_ticket(db: AsyncSession, ticket_id: int):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalar_one_or_none()


async def create_ticket(db: AsyncSession, ticket_in: TicketCreate):
    new_ticket = Ticket(**ticket_in.model_dump())
    db.add(new_ticket)
    try:
        await db.commit()
        await db.refresh(new_ticket)
        return new_ticket
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_ticket(db: AsyncSession, ticket_id: int, ticket_in: TicketUpdate):
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise Exception("Ticket not found")
    for key, value in ticket_in.model_dump(exclude_unset=True).items():
        setattr(ticket, key, value)
    try:
        await db.commit()
        await db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def delete_ticket(db: AsyncSession, ticket_id: int):
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise Exception("Ticket not found")
    try:
        db.delete(ticket)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
