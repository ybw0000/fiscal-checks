from fastapi import FastAPI

from src.base import base_router
from src.checks import checks_router
from src.conf.settings import settings
from src.users import users_router


def init_routers(app: FastAPI) -> None:
    app.include_router(router=base_router, prefix=settings.PREFIX, tags=["Base"])
    app.include_router(router=users_router, prefix=settings.PREFIX, tags=["Users"])
    app.include_router(router=checks_router, prefix=settings.PREFIX, tags=["Checks"])
