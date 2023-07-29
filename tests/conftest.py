from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from .fixtures import data as d

try:
    from app.main import app
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружен объект приложения `app`.'
        'Проверьте и поправьте: он должен быть доступен в модуле `app.main`.')

try:
    from app.core import Base, get_async_session
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружены объекты `Base, get_async_session`. Они должны находиться в модуле `app.core.db`.')

try:
    from app.crud.base import CRUDBase  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `CRUDBase`. Он должен находиться в модуле `app.crud.base`')

try:
    from app.crud.crud import MenuCRUD  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `MenuCRUD`. Он должен находиться в модуле `app.crud.crud`')

try:
    from app.models import Menu  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `Menu`. Он должен находиться в модуле `app.models`')

try:
    from app.models import Submenu  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `Submenu`. Он должен находиться в модуле `app.models`')

try:
    from app.models import Dish  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `Dish`. Он должен находиться в модуле `app.models`')

try:
    from app.schemas import MenuIn, MenuOut  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найдены объекты `MenuIn` и/или `MenuOut`. Они должны находиться в модуле `app.schemas`')

try:
    from app.crud import menu_crud, submenu_crud, dish_crud  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найдены объекты `menu_crud, submenu_crud, dish_crud`. Они должны находиться в модуле `app.crud`')


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL,
                             connect_args={"check_same_thread": False})

TestingSessionLocal = async_sessionmaker(expire_on_commit=False,
                                         autocommit=False,
                                         autoflush=False,
                                         bind=engine)


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def get_test_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def menu(async_client: httpx.AsyncClient) -> Response:
    yield await async_client.post(d.ENDPOINT_MENU, json=d.MENU_POST_PAYLOAD)   


@pytest_asyncio.fixture
async def submenu(async_client: httpx.AsyncClient, menu) -> Response:
    assert menu.status_code == 201, (menu.headers, menu.content)
    yield await async_client.post(d.ENDPOINT_SUBMENU, json=d.SUBMENU_POST_PAYLOAD)


@pytest_asyncio.fixture
async def dish(async_client: httpx.AsyncClient, submenu) -> Response:
    assert submenu.status_code == 201, (submenu.headers, submenu.content)
    yield await async_client.post(d.ENDPOINT_DISH, json=d.DISH_POST_PAYLOAD)


@pytest_asyncio.fixture
async def get_menu_crud():
    yield menu_crud


@pytest_asyncio.fixture
async def get_submenu_crud():
    yield submenu_crud


@pytest_asyncio.fixture
async def get_dish_crud():
    yield dish_crud