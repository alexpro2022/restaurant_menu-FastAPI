from ..conftest import pytest_mark_anyio
from ..fixtures import data as d

pytestmark = pytest_mark_anyio


async def test_delete_menu(menu, get_menu_crud):
    assert await get_menu_crud.delete(menu.json()['id']) == d.DELETED_MENU


async def test_delete_submenu(submenu, get_submenu_crud):
    assert await get_submenu_crud.delete(submenu.json()['id']) == d.DELETED_SUBMENU


async def test_delete_dish(dish, get_dish_crud):
    assert await get_dish_crud.delete(dish.json()['id']) == d.DELETED_DISH
