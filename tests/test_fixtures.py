import asyncio

from httpx import AsyncClient

from .conftest import CRUDBase


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


def test_get_menu_crud(get_menu_crud):
    assert isinstance(get_menu_crud, CRUDBase)


def test_get_submenu_crud(get_submenu_crud):
    assert isinstance(get_submenu_crud, CRUDBase)


def test_get_dish_crud(get_dish_crud):
    assert isinstance(get_dish_crud, CRUDBase)


async def test_provided_loop_is_running_loop(event_loop):
    assert event_loop is asyncio.get_running_loop()
