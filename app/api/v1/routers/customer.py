from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customer as customer_service

router = APIRouter(prefix="/customer", tags=["customer"])


@router.post("/", response_model=CustomerRead)
async def create_customer(
    customer: CustomerCreate, db: AsyncSession = Depends(get_session)
):
    try:
        return await customer_service.create_customer(db, customer)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"could not create customer: {str(e)}"
        )


@router.get("/", response_model=list[CustomerRead])
async def list_customers(db: AsyncSession = Depends(get_session)):
    return await customer_service.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_session)):
    customer = await customer_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: int, customer: CustomerUpdate, db: AsyncSession = Depends(get_session)
):
    customer = await customer_service.update_customer(db, customer_id, customer)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_session)):
    success = await customer_service.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"deleted": True, "customer_id": customer_id}



