from datetime import datetime
from decimal import Decimal

from markupsafe import Markup
from sqlalchemy.orm import selectinload

from src.base.models import BaseModel
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

    async def get_check(self, id: int) -> Check | BaseModel:
        return await self.fetch_one(
            filters=(self.MODEL.id == id,),
            options=(
                selectinload(self.MODEL.products),
                selectinload(self.MODEL.payment),
                selectinload(self.MODEL.user),
            ),
        )


class MarkupService:
    def __init__(self, check: Check = None):
        self.check = check
        if check:
            self.max_symbols = check.user.check_symbols or 50

    class ALIGN:
        LEFT = "left"
        RIGHT = "right"
        CENTER = "center"

    def get_spaces(self, text: str, align=ALIGN.LEFT) -> tuple[str, str]:
        left_spaces = ""
        right_spaces = ""
        empty_space_count = self.max_symbols - len(text)

        if align == self.ALIGN.LEFT:
            return left_spaces, " " * empty_space_count
        elif align == self.ALIGN.RIGHT:
            return " " * empty_space_count, right_spaces
        elif align == self.ALIGN.CENTER:
            return " " * int(empty_space_count / 2), " " * int(empty_space_count / 2)

    def get_line(self, text, align=ALIGN.LEFT):
        text = text.strip()
        left_spaces, right_spaces = self.get_spaces(text, align)
        return f"{left_spaces}{text}{right_spaces}"

    def split_text(self, text: str, indentation: int = 0) -> list[str]:
        return [
            text[i : i + self.max_symbols - indentation] for i in range(0, len(text), self.max_symbols - indentation)
        ]

    def build_header(self):
        base_header = f"ФОП {self.check.user.last_name} {self.check.user.first_name}"
        align = self.ALIGN.CENTER
        markup_lines = []
        # build header
        if len(base_header) > self.max_symbols:
            parts = base_header.split(" ")
            part_line = ""
            for part in parts:
                if len(" ".join((part_line, part))) <= self.max_symbols:
                    part_line = " ".join((part_line, part))
                else:
                    markup_lines.append(self.get_line(part_line, align)) if part_line else ""
                    part_line = ""
                    if len(part) <= self.max_symbols:
                        part_line = part
                    else:
                        for part_sub in self.split_text(part):
                            markup_lines.append(self.get_line(part_sub, align))
            else:
                markup_lines.append(self.get_line(part_line, align))
        else:
            markup_lines.append(self.get_line(base_header, align))

        markup_lines.append("=" * self.max_symbols)

        return markup_lines

    def build_products(self):
        markup_lines = []

        for product in self.check.products:
            total_price = f"= {round(product.total, 2)}"
            if len(product.name) + len(total_price) <= self.max_symbols:
                markup_lines.append(self.get_line(product.name))
            else:
                markup_lines.extend(self.split_text(product.name, len(total_price)))

            product_price_formation = f"{product.quantity} x {product.price}"
            base_product_details_line = (
                f"{product_price_formation}{self.get_spaces(product_price_formation+total_price)[1]}{total_price}"
            )

            if len(base_product_details_line) <= self.max_symbols:
                markup_lines.append(base_product_details_line)
            else:
                product_price_formation = product_price_formation.split(" ")
                lines = list()
                for part in product_price_formation:
                    lines.extend(self.split_text(part, len(total_price)))
                lines[-1] = f"{lines[-1]}{self.get_spaces(lines[-1]+total_price)[1]}{total_price}"
                markup_lines.extend(lines)

            if self.check.products[-1] != product:
                markup_lines.append("-" * self.max_symbols)

        markup_lines.append("=" * self.max_symbols)
        return markup_lines

    def build_payment(self):
        markup_lines = []

        check_amount = str(round(self.check.total, 2))
        check_amount_line = f"Сума{self.get_spaces('Сума'+check_amount)[1]}{check_amount}"
        markup_lines.append(check_amount_line)

        payment_amount_type = "Картка" if self.check.payment.type == "card" else "Готівка"
        payment_amount = str(round(self.check.payment.amount, 2))
        payment_amount_line = (
            f"{payment_amount_type}{self.get_spaces(payment_amount_type+payment_amount)[1]}{payment_amount}"
        )
        markup_lines.append(payment_amount_line)

        rest_amount = str(round(self.check.rest, 2))
        rest_amount_line = f"Решта{self.get_spaces('Решта'+rest_amount)[1]}{rest_amount}"
        markup_lines.append(rest_amount_line)

        markup_lines.append("=" * self.max_symbols)
        return markup_lines

    def build_footer(self):
        markup_lines = []
        align = self.ALIGN.CENTER

        markup_lines.append(self.get_line("Дякуємо за покупку!", align))
        markup_lines.append(self.get_line(str(self.check.created_at.replace(microsecond=0)), align))
        markup_lines.extend(self.get_line(part, align) for part in self.split_text(self.check.comment))

        return markup_lines

    def build_markup(self) -> Markup:
        if not self.check:
            return Markup()

        markup_lines = self.build_header()
        markup_lines.extend(self.build_products())
        markup_lines.extend(self.build_payment())
        markup_lines.extend(self.build_footer())

        return Markup("<br>".join(markup_lines))
