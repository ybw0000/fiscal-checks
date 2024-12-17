from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator

from src.checks.models import PaymentTypeEnum
from src.conf.settings import settings


class CheckProductDTOCreateSchema(BaseModel):
    name: str
    price: Decimal
    quantity: Decimal


class CheckPaymentDTOCreateSchema(BaseModel):
    type: PaymentTypeEnum
    amount: Decimal


class CheckDTOCreateSchema(BaseModel):
    products: list[CheckProductDTOCreateSchema]
    payment: CheckPaymentDTOCreateSchema
    comment: str | None = None


class CheckProductDTOReadSchema(BaseModel):
    name: str
    price: Decimal
    quantity: Decimal
    total: Decimal

    model_config = ConfigDict(from_attributes=True)


class CheckPaymentDTOReadSchema(BaseModel):
    type: PaymentTypeEnum
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class CheckDTOResponseSchema(BaseModel):
    id: int
    products: list[CheckProductDTOReadSchema]
    payment: CheckPaymentDTOReadSchema
    comment: str | None = None
    total: Decimal
    rest: Decimal
    created_at: datetime
    updated_at: datetime
    url: AnyHttpUrl | str | None = Field(None, description="URL to check details")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def set_url(self):
        self.url = f"http://localhost:{settings.PORT}/api/v1/checks/{self.id}"
        return self


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "-created_at"] = "created_at"
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    total_gte: Decimal | None = None
    total_lte: Decimal | None = None
    payment_type: PaymentTypeEnum | None = None


class ChecksWithPaginationResponseSchema(BaseModel):
    total: int
    results: list[CheckDTOResponseSchema]
