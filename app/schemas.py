from enum import Enum
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperation(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    balance: Decimal
