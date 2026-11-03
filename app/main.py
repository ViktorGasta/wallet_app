import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import WalletOperation, WalletResponse
from app.crud import get_wallet, handle_wallet_operation

app = FastAPI(title="Wallet REST API")


@app.post(
    "/api/v1/wallets/{wallet_uuid}/operation",
    response_model=WalletResponse,
)
async def wallet_operation(
    wallet_uuid: uuid.UUID,
    operation: WalletOperation,
    db: AsyncSession = Depends(get_db),
):
    return await handle_wallet_operation(
        db=db,
        wallet_uuid=wallet_uuid,
        op_type=operation.operation_type,
        amount=operation.amount,
    )


@app.get(
    "/api/v1/wallets/{wallet_uuid}",
    response_model=WalletResponse,
)
async def get_wallet_balance(
    wallet_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    wallet = await get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet
