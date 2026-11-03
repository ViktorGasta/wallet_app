import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Wallet
from app.schemas import OperationType


async def get_wallet(
        db: AsyncSession,
        wallet_uuid: uuid.UUID
) -> Wallet | None:
    """Получить информацию о кошельке без блокировки строки."""

    result = await db.execute(select(Wallet).where(Wallet.id == wallet_uuid))
    return result.scalars().first()


async def create_wallet(
        db: AsyncSession,
        initial_balance: Decimal = Decimal("0.0")
) -> Wallet:
    """Создать новый кошелек с заданным балансом."""

    if initial_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Initial balance cannot be negative",
        )
    db_wallet = Wallet(id=uuid.uuid4(), balance=initial_balance)
    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet


async def handle_wallet_operation(
    db: AsyncSession,
    wallet_uuid: uuid.UUID,
    op_type: OperationType,
    amount: Decimal
) -> Wallet:
    """
    Конкурентное изменение баланса кошелька с использованием SELECT FOR UPDATE.
    """

    query = (
        select(Wallet)
        .where(Wallet.id == wallet_uuid)
        .with_for_update()
    )
    result = await db.execute(query)
    wallet = result.scalars().first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    if op_type == OperationType.DEPOSIT:
        wallet.balance += amount
    elif op_type == OperationType.WITHDRAW:
        if wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )
        wallet.balance -= amount

    await db.commit()
    await db.refresh(wallet)
    return wallet
