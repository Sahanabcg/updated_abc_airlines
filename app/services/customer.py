from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import User
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def list_customers(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_customer(db: AsyncSession, customer_id: int):
    result = await db.execute(select(User).where(User.id == customer_id))
    return result.scalar_one_or_none()


async def create_customer(db: AsyncSession, customer_in: CustomerCreate):
    new_customer = User(**customer_in.model_dump())
    db.add(new_customer)
    try:
        await db.commit()
        await db.refresh(new_customer)
        return new_customer
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_customer(
    db: AsyncSession, customer_id: int, customer_in: CustomerUpdate
):
    customer = await get_customer(db, customer_id)
    if not customer:
        raise Exception("Customer not found")
    for key, value in customer_in.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    try:
        await db.commit()
        await db.refresh(customer)
        return customer
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def delete_customer(db: AsyncSession, customer_id: int):
    customer = await get_customer(db, customer_id)
    if not customer:
        raise Exception("Customer not found")
    try:
        await db.delete(customer)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise e



