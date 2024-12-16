import datetime

from typing import Any
from typing import Callable
from typing import Dict
from typing import Sequence
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

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

    async def fetch(
        self,
        filters: Sequence,
        options: Sequence = (),
        limit: int = None,
        offset: int = None,
        order_by: str = None,
    ) -> Sequence[BaseModel]:
        """Fetch all obj from database"""
        query = select(self.MODEL).where(*filters).options(*options)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        if order_by:
            if order_by.startswith("-"):
                order_by = order_by[1:]
                order_by = self.MODEL.__table__.columns[order_by].desc()
            else:
                order_by = self.MODEL.__table__.columns[order_by]
            query = query.order_by(order_by)
        return await self._db_call(self.session.scalars, query)

    async def count(self, filters: Sequence):
        """
        Counts the number of entries in the database that satisfy the given filters.
        """
        query = select(count(self.MODEL.id)).where(*filters)
        return await self._db_call(self.session.scalar, query)
