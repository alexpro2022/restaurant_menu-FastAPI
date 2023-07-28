from typing import AsyncGenerator

import pytest

from .conftest import get_async_session


@pytest.mark.anyio
async def test_get_async_session():
    assert isinstance(get_async_session(), AsyncGenerator)

