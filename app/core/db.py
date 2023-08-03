from typing import AsyncGenerator

from sqlalchemy import MetaData, String
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)

from app.core import settings


md = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})


class Base(DeclarativeBase):
    metadata = md

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    description: Mapped[str]

    def __repr__(self) -> str:
        return (f'\nid: {self.id},'
                f'\ntitle: {self.title},'
                f'\ndescription: {self.description},\n')


engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as async_session:
        yield async_session
