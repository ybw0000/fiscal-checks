import enum

from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.base.models import BaseModel
from src.users.models import User


class PaymentTypeEnum(enum.Enum):
    cash = "cash"
    card = "card"


class CheckProduct(BaseModel):
    __tablename__ = "check_products"

    name: Mapped[str]
    price: Mapped[Decimal]
    quantity: Mapped[Decimal]
    total: Mapped[Decimal]
    check_id: Mapped[int] = mapped_column(ForeignKey("checks.id"))

    check: Mapped["Check"] = relationship("Check", back_populates="products")


class CheckPayment(BaseModel):
    __tablename__ = "check_payments"

    type: Mapped[PaymentTypeEnum]
    amount: Mapped[Decimal]
    check_id: Mapped[int] = mapped_column(ForeignKey("checks.id"))

    check: Mapped["Check"] = relationship("Check", back_populates="payment")


class Check(BaseModel):
    __tablename__ = "checks"

    comment: Mapped[Optional[str]] = mapped_column(server_default="Тут могло бути передбачення з Сільпо))")
    total: Mapped[Decimal]
    rest: Mapped[Decimal]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", backref="checks")
    payment: Mapped["CheckPayment"] = relationship("CheckPayment", back_populates="check")
    products: Mapped[list["CheckProduct"]] = relationship(
        "CheckProduct",
        back_populates="check",
        cascade="all, delete-orphan",
    )
