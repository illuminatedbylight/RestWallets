from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from decimal import Decimal

from database import get_session
from models import Wallet, OperationRequest, OperationType

app = FastAPI(title="Wallet API")


@app.post("/api/v1/wallets")
async def create_wallet(session: AsyncSession = Depends(get_session)):
    new_wallet = Wallet(id=uuid4(), balance=Decimal("0.00"))

    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)

    return {"wallet_id": str(new_wallet.id), "balance": str(new_wallet.balance)}


@app.post("/api/v1/wallets/{wallet_uuid}/operation")
async def wallet_operation(
    wallet_uuid: UUID,
    operation: OperationRequest,
    session: AsyncSession = Depends(get_session),
):

    result = await session.execute(
        select(Wallet).where(Wallet.id == wallet_uuid).with_for_update()
    )
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if operation.operation_type == OperationType.DEPOSIT:
        wallet.balance += operation.amount
    else:
        if wallet.balance < operation.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        wallet.balance -= operation.amount

    await session.commit()

    return {
        "status": "success",
        "wallet_id": str(wallet_uuid),
        "balance": str(wallet.balance),
    }


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet_balance(
    wallet_uuid: UUID, session: AsyncSession = Depends(get_session)
):
    wallet = await session.get(Wallet, wallet_uuid)

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {"wallet_id": str(wallet.id), "balance": str(wallet.balance)}
