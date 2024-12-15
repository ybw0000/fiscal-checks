import enum

from typing import Optional

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.base.models import BaseModel


class PaymentTypeEnum(enum.Enum):
    cash = "cash"
    card = "card"


class Check(BaseModel):
    __tablename__ = "checks"

    products: Mapped[ARRAY[dict]]
    payment_type: Mapped[Enum[PaymentTypeEnum]]
    comment: Mapped[Optional[str]] = mapped_column(server_default="Тут могло бути передбачення з Сільпо))")
