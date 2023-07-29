import pytest

from httpx import AsyncClient

from .conftest import Dish, Menu, Submenu
from .fixtures import data as d

@pytest.mark.asyncio
async def test_scenario(dish, async_client: AsyncClient, get_test_session, get_menu_crud, get_submenu_crud, get_dish_crud):

    # fixture dish - Создает меню + Создает подменю + Создает блюдо 1
    counter = 0
    for crud, model in (
        (get_menu_crud, Menu),
        (get_submenu_crud, Submenu),
        (get_dish_crud, Dish),
    ):
        counter += 1
        items = await crud.get_all(get_test_session)
        assert isinstance(items, list)
        assert len(items) == 1
        assert isinstance(items[0], model)
    assert counter == 3

    # Создает блюдо 2   
    await async_client.post(d.ENDPOINT_DISH, json=d.DISH_PATCH_PAYLOAD)
    dishes = await get_dish_crud.get_all(get_test_session)
    assert len(dishes) == 2

    # Просматривает определенное меню
    #menu = await get_menu_crud.get_or_404(get_test_session, 1)
    #assert menu.get_submenus_count() == 1
    #assert menu.get_dishes_count() == 2
    response = await async_client.get(f'{d.ENDPOINT_MENU}/{d.ID}')
    assert response.status_code == 200
    assert response.json()['submenus_count'] == 1
    assert response.json()['dishes_count'] == 2


    # Просматривает определенное подменю
    submenu = await get_submenu_crud.get_or_404(get_test_session, 1)
    assert submenu.get_dishes_count() == 2
    response = await async_client.get(f'{d.ENDPOINT_SUBMENU}/{d.ID}')
    assert response.status_code == 200
    assert response.json()['dishes_count'] == 2


    # Удаляет подменю
    assert await get_menu_crud.get_all(get_test_session)
    assert await get_submenu_crud.get_all(get_test_session)
    assert await get_dish_crud.get_all(get_test_session)
    response = await async_client.delete(f'{d.ENDPOINT_SUBMENU}/{d.ID}')
    assert response.status_code == 200
    assert await get_menu_crud.get_all(get_test_session)
    assert not await get_submenu_crud.get_all(get_test_session)
    assert not await get_dish_crud.get_all(get_test_session)

    # Просматривает список подменю
    response = await async_client.get(d.ENDPOINT_SUBMENU)
    assert response.status_code == 200
    assert response.json() == []

    # Просматривает список блюд
    response = await async_client.get(d.ENDPOINT_DISH)
    assert response.status_code == 200
    assert response.json() == []

    # Просматривает определенное меню
    response = await async_client.get(f'{d.ENDPOINT_MENU}/{d.ID}')
    assert response.status_code == 200
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0

    # Удаляет меню
    response = await async_client.delete(f'{d.ENDPOINT_MENU}/{d.ID}')
    assert response.status_code == 200

    # Просматривает список меню
    response = await async_client.get(d.ENDPOINT_MENU)
    assert response.status_code == 200
    assert response.json() == []