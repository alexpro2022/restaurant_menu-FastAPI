from ..conftest import pytest_mark_anyio


@pytest_mark_anyio
async def test_delete_menu(menu, get_menu_crud):
    expected_response = {'status': True, 'message': 'The menu has been deleted'}
    assert await get_menu_crud.delete(menu.json()['id']) == expected_response


@pytest_mark_anyio
async def test_delete_submenu(submenu, get_submenu_crud):
    expected_response = {'status': True, 'message': 'The submenu has been deleted'}
    assert await get_submenu_crud.delete(submenu.json()['id']) == expected_response


@pytest_mark_anyio
async def test_delete_dish(dish, get_dish_crud):
    expected_response = {'status': True, 'message': 'The dish has been deleted'}
    assert await get_dish_crud.delete(dish.json()['id']) == expected_response
