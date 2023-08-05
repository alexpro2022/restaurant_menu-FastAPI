from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import get_async_session, pytest_mark_anyio


@pytest_mark_anyio
async def test_get_async_session():
    assert isinstance(get_async_session(), AsyncGenerator)
    asession = await get_async_session().__anext__()
    assert isinstance(asession, AsyncSession)
