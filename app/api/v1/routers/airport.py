from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.airport import AirportCreate, AirportRead, AirportUpdate
from app.services import airport as airport_service

router = APIRouter(prefix="/airport", tags=["airport"])


@router.post("/", response_model=AirportRead)
async def create_airport(
    airport: AirportCreate, db: AsyncSession = Depends(get_session)
):
    try:
        return await airport_service.create_airport(db, airport)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not create airport: {str(e)}"
        )


@router.get("/", response_model=list[AirportRead])
async def list_airports(db: AsyncSession = Depends(get_session)):
    return await airport_service.list_airports(db)


@router.get("/{code}", response_model=AirportRead)
async def get_airport(code: str, db: AsyncSession = Depends(get_session)):
    airport = await airport_service.get_airport(db, code)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport


@router.patch("/{code}", response_model=AirportRead)
async def update_airport(
    code: str, airport: AirportUpdate, db: AsyncSession = Depends(get_session)
):
    airport = await airport_service.update_airport(db, code, airport)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport


@router.delete("/{code}", status_code=200)
async def delete_airport(code: str, db: AsyncSession = Depends(get_session)):
    success = await airport_service.delete_airport(db, code)
    if not success:
        raise HTTPException(status_code=404, detail="Airport not found")
    return {"deleted": True, "airport_code": code}
