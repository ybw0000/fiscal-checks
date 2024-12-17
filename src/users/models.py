from typing_extensions import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.base.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    check_symbols: Mapped[Optional[int]]
