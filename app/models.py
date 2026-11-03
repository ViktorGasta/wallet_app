import uuid
from sqlalchemy import Column, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    balance = Column(Numeric(14, 2), nullable=False, default=0.0)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_positive"),
    )
