import asyncio

from fakeredis import aioredis
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .conftest import (
    DishRepository,
    MenuRepository,
    SubmenuRepository,
    pytest_mark_anyio,
)


@pytest_mark_anyio
async def test_provided_loop_is_running_loop(event_loop):
    assert event_loop is asyncio.get_running_loop()


# --- Fixtures for endpoints testing -----------------------------------------------
def test_async_client(async_client):
    assert isinstance(async_client, AsyncClient)


def test_menu(menu):
    assert menu.status_code == 201, (menu.headers, menu.content)


def test_menu_dynamic(request):
    menu = request.getfixturevalue('menu')
    assert menu.status_code == 201, (menu.headers, menu.content)


def test_submenu(submenu):
    assert submenu.status_code == 201, (submenu.headers, submenu.content)


def test_submenu_dynamic(request):
    submenu = request.getfixturevalue('submenu')
    assert submenu.status_code == 201, (submenu.headers, submenu.content)


def test_dish(dish):
    assert dish.status_code == 201, (dish.headers, dish.content)


def test_dish_dynamic(request):
    dish = request.getfixturevalue('dish')
    assert dish.status_code == 201, (dish.headers, dish.content)


# --- Fixtures for repository testing -----------------------------------------------
@pytest_mark_anyio
async def test_get_test_redis(get_test_redis):
    assert isinstance(get_test_redis, aioredis.FakeRedis)
    assert await get_test_redis.set('key', 'value')
    assert await get_test_redis.get('key') == b'value'
    assert await get_test_redis.set('key', 'value2')
    assert await get_test_redis.get('key') == b'value2'
    assert await get_test_redis.delete('key')
    assert await get_test_redis.get('key') == None


def test_get_test_session(get_test_session):
    assert isinstance(get_test_session, AsyncSession)


def test_get_menu_crud(get_menu_crud):
    assert isinstance(get_menu_crud, MenuRepository)


def test_get_submenu_crud(get_submenu_crud):
    assert isinstance(get_submenu_crud, SubmenuRepository)


def test_get_dish_crud(get_dish_crud):
    assert isinstance(get_dish_crud, DishRepository)
