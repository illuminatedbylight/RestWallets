from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID
from decimal import Decimal
from uuid import UUID as UUIDType
from pydantic import BaseModel, Field
from enum import Enum


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(..., gt=0, description="Amount must be a positive number")
