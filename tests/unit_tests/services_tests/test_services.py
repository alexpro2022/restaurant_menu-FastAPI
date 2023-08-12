from tests.fixtures import data as d


async def

'''
async def test_delete_menu(menu, get_menu_service):
    assert await get_menu_service.delete(menu.json()['id']) == d.DELETED_MENU


async def test_delete_submenu(submenu, get_submenu_service):
    assert await get_submenu_service.delete(submenu.json()['id']) == d.DELETED_SUBMENU


async def test_delete_dish(dish, get_dish_service):
    assert await get_dish_service.delete(dish.json()['id']) == d.DELETED_DISH
'''
