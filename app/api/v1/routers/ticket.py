from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services import ticket as ticket_service

router = APIRouter(prefix="/ticket", tags=["ticket"])


@router.post("/", response_model=TicketRead)
async def create_ticket(ticket: TicketCreate, db: AsyncSession = Depends(get_session)):
    try:
        return await ticket_service.create_ticket(db, ticket)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not create ticket: {str(e)}"
        )


@router.get("/", response_model=list[TicketRead])
async def list_tickets(db: AsyncSession = Depends(get_session)):
    return await ticket_service.list_tickets(db)


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_session)):
    ticket = await ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: int, ticket: TicketUpdate, db: AsyncSession = Depends(get_session)
):
    ticket = await ticket_service.update_ticket(db, ticket_id, ticket)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_session)):
    success = await ticket_service.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"deleted": True, "ticket_id": ticket_id}
