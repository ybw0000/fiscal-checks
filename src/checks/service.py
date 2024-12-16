from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import selectinload

from src.base.service import BaseService
from src.checks.models import Check
from src.checks.models import CheckPayment
from src.checks.models import CheckProduct
from src.checks.schemas import CheckDTOCreateSchema
from src.checks.schemas import ChecksWithPaginationResponseSchema
from src.checks.schemas import FilterParams
from src.users.models import User


class CheckService(BaseService):
    MODEL = Check

    async def create_check(self, user: User, request_data: CheckDTOCreateSchema) -> Check:
        now = datetime.now(tz=None)

        products = [
            CheckProduct(
                name=product.name,
                price=product.price,
                quantity=product.quantity,
                total=Decimal(product.price * product.quantity),
                updated_at=now,
            )
            for product in request_data.products
        ]
        payment = CheckPayment(
            type=request_data.payment.type,
            amount=request_data.payment.amount,
            updated_at=now,
        )
        total_price = Decimal(sum([product.total for product in products]))
        check = self.MODEL(
            user=user,
            products=products,
            payment=payment,
            comment=request_data.comment,
            total=total_price,
            rest=Decimal(payment.amount - total_price),
        )

        check: Check = await self.insert_obj(check)
        return check

    async def get_user_checks(self, user: User, filter_params: FilterParams) -> ChecksWithPaginationResponseSchema:
        filters = (self.MODEL.user_id == user.id,)

        if filter_params.created_at_gte:
            filters += (self.MODEL.created_at >= filter_params.created_at_gte,)
        if filter_params.created_at_lte:
            filters += (self.MODEL.created_at <= filter_params.created_at_lte,)
        if filter_params.total_gte:
            filters += (self.MODEL.total >= filter_params.total_gte,)
        if filter_params.total_lte:
            filters += (self.MODEL.total <= filter_params.total_lte,)
        if filter_params.payment_type:
            filters += (self.MODEL.payment.has(CheckPayment.type == filter_params.payment_type),)

        options = (selectinload(self.MODEL.products), selectinload(self.MODEL.payment))

        total = await self.count(filters)
        items = await self.fetch(
            filters,
            options,
            filter_params.limit,
            filter_params.offset,
            filter_params.order_by,
        )
        return ChecksWithPaginationResponseSchema(total=total, results=items)

    async def get_check(self, id: int) -> Check:
        return await self.fetch_one(
            filters=(self.MODEL.id == id,),
            options=(
                selectinload(self.MODEL.products),
                selectinload(self.MODEL.payment),
                selectinload(self.MODEL.user),
            ),
        )
