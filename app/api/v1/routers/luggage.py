from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.luggage import LuggageCreate, LuggageRead, LuggageUpdate
from app.services import luggage as luggage_service

router = APIRouter(prefix="/luggage", tags=["luggage"])


@router.post("/", response_model=LuggageRead)
async def create_luggage(
    Luggage: LuggageCreate, db: AsyncSession = Depends(get_session)
):
    try:
        return await luggage_service.create_luggage(db, Luggage)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not create luggage: {str(e)}"
        )


@router.get("/", response_model=list[LuggageRead])
async def list_luggages(db: AsyncSession = Depends(get_session)):
    return await luggage_service.list_luggages(db)


@router.get("/{luggage_id}", response_model=LuggageRead)
async def get_luggage(luggage_id: int, db: AsyncSession = Depends(get_session)):
    luggage = await luggage_service.get_luggage(db, luggage_id)
    if not luggage:
        raise HTTPException(status_code=404, detail="Luggage not found")
    return luggage


@router.patch("/{luggage_id}", response_model=LuggageRead)
async def update_Luggage(
    luggage_id: int, luggage: LuggageUpdate, db: AsyncSession = Depends(get_session)
):
    luggage = await luggage_service.update_luggage(db, luggage_id, luggage)
    if not luggage:
        raise HTTPException(status_code=404, detail="Luggage not found")
    return luggage


@router.delete("/{luggage_id}", status_code=status.HTTP_200_OK)
async def delete_luggage(luggage_id: int, db: AsyncSession = Depends(get_session)):
    success = await luggage_service.delete_luggage(db, luggage_id)
    if not success:
        raise HTTPException(status_code=404, detail="Luggage not found")
    return {"deleted": True, "luggage_id": luggage_id}
