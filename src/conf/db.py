from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from src.conf.settings import settings


async_session = sessionmaker(None, expire_on_commit=False, class_=AsyncSession)
session_factory = sessionmaker(None)

sync_engine = create_engine(url=settings.sqlalchemy_database_uri)
session_factory.configure(bind=sync_engine)
Session = scoped_session(session_factory)
