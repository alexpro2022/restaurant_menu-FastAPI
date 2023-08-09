from typing import AsyncGenerator

from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import get_aioredis, get_async_session, pytest_mark_anyio

pytestmark = pytest_mark_anyio


async def test_get_async_session():
    agen = get_async_session()
    assert isinstance(agen, AsyncGenerator)
    asession = await agen.__anext__()
    assert isinstance(asession, AsyncSession)


async def test_get_aioredis():
    assert isinstance(get_aioredis(), Redis)
