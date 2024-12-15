import datetime

from typing import Any
from typing import Callable
from typing import Dict
from typing import Sequence
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.models import BaseModel


class BaseService:
    MODEL: Type[BaseModel]

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _db_call(function: Callable, query: Any) -> Any:
        """Call DB with handle async mode"""
        return await function(query)

    async def fetch_one(self, filters: Sequence, options: Sequence = ()) -> BaseModel | None:
        """Fetch one obj from database"""
        query = select(self.MODEL).where(*filters).options(*options).limit(1)
        return await self._db_call(self.session.scalar, query)

    async def _commit(self) -> Any:
        """Call DB with handle async mode"""
        return await self.session.commit()

    async def insert_obj(self, obj: BaseModel) -> BaseModel:
        """Insert new obj to DB"""
        now = datetime.datetime.now(tz=None)
        if hasattr(self.MODEL, "updated_at"):
            obj.updated_at = now
        self.session.add(obj)
        await self._commit()
        return obj

    async def insert(self, values: Dict) -> BaseModel:
        """Insert new obj to DB"""
        return await self.insert_obj(self.MODEL(**values))

    async def asd(self):
        re
