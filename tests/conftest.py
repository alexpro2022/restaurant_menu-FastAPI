import aioredis
import httpx
import pytest
import pytest_asyncio
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import Base, get_async_session
from app.main import app
from app.models import Dish, Menu, Submenu  # noqa
from app.repository import DishRepository, MenuRepository, SubmenuRepository
from app.repository.base import CRUDBaseRepository  # noqa
from app.schemas import MenuIn, MenuOut  # noqa

from .fixtures import data as d

pytest_mark_anyio = pytest.mark.anyio

engine = create_async_engine('sqlite+aiosqlite:///./test.db',
                             connect_args={'check_same_thread': False})

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


@pytest_asyncio.fixture()
async def redis():
    redis = await aioredis.from_url(
        'redis://localhost', encoding='utf-8', decode_responses=True
    )
    yield redis
    redis.close()


@pytest_asyncio.fixture
async def get_test_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def menu(async_client: httpx.AsyncClient) -> Response:
    menu = await async_client.post(d.ENDPOINT_MENU, json=d.MENU_POST_PAYLOAD)
    assert menu.status_code == 201, (menu.headers, menu.content)
    yield menu


@pytest_asyncio.fixture
async def submenu(async_client: httpx.AsyncClient, menu) -> Response:
    assert menu.status_code == 201, (menu.headers, menu.content)
    submenu = await async_client.post(d.ENDPOINT_SUBMENU, json=d.SUBMENU_POST_PAYLOAD)
    assert submenu.status_code == 201, (submenu.headers, submenu.content)
    yield submenu


@pytest_asyncio.fixture
async def dish(async_client: httpx.AsyncClient, submenu) -> Response:
    assert submenu.status_code == 201, (submenu.headers, submenu.content)
    dish = await async_client.post(d.ENDPOINT_DISH, json=d.DISH_POST_PAYLOAD)
    assert dish.status_code == 201, (dish.headers, dish.content)
    yield dish


@pytest_asyncio.fixture
async def get_menu_crud(get_test_session):
    yield MenuRepository(get_test_session)


@pytest_asyncio.fixture
async def get_submenu_crud(get_test_session):
    yield SubmenuRepository(get_test_session)


@pytest_asyncio.fixture
async def get_dish_crud(get_test_session):
    yield DishRepository(get_test_session)
