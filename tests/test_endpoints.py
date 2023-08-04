import pytest

from . import utils as u
from .conftest import pytest_mark_anyio
from .fixtures import data as d
from .fixtures.endpoints_testlib import not_allowed_methods_test, standard_tests

DELETE, GET, POST, PUT, PATCH = 'DELETE', 'GET', 'POST', 'PUT', 'PATCH'

pytestmark = pytest_mark_anyio


@pytest.mark.parametrize('endpoint', (d.ENDPOINT_DISH, d.ENDPOINT_MENU, d.ENDPOINT_SUBMENU))
async def test_not_allowed_method(async_client, endpoint):
    await not_allowed_methods_test(async_client, (PUT,), endpoint)


@pytest.mark.parametrize('endpoint', (d.ENDPOINT_DISH, d.ENDPOINT_MENU, d.ENDPOINT_SUBMENU))
async def test_get_all_returns_empty_list(async_client, endpoint):
    result = await async_client.get(endpoint)
    assert result.json() == []


@pytest.mark.parametrize('method, endpoint, path_param, payload, msg_already_exists, msg_not_found, check_func', (
    (GET, d.ENDPOINT_MENU, None, None, *d.MENU_MSG_PACK, u.check_menu_list),
    (GET, d.ENDPOINT_MENU, d.ID, None, *d.MENU_MSG_PACK, u.check_menu),
    (PATCH, d.ENDPOINT_MENU, d.ID, d.MENU_PATCH_PAYLOAD, *d.MENU_MSG_PACK, u.check_menu_updated),
    (DELETE, d.ENDPOINT_MENU, d.ID, None, *d.MENU_MSG_PACK, u.check_menu_deleted),
    # -------------------------------------------------------------------------------------------------
    (GET, d.ENDPOINT_SUBMENU, None, None, *d.SUBMENU_MSG_PACK, u.check_submenu_list),
    (GET, d.ENDPOINT_SUBMENU, d.ID, None, *d.SUBMENU_MSG_PACK, u.check_submenu),
    (PATCH, d.ENDPOINT_SUBMENU, d.ID, d.SUBMENU_PATCH_PAYLOAD, *d.SUBMENU_MSG_PACK, u.check_submenu_updated),
    (DELETE, d.ENDPOINT_SUBMENU, d.ID, None, *d.SUBMENU_MSG_PACK, u.check_submenu_deleted),
    # -------------------------------------------------------------------------------------------------
    (GET, d.ENDPOINT_DISH, None, None, *d.DISH_MSG_PACK, u.check_dish_list),
    (GET, d.ENDPOINT_DISH, d.ID, None, *d.DISH_MSG_PACK, u.check_dish),
    (PATCH, d.ENDPOINT_DISH, d.ID, d.DISH_PATCH_PAYLOAD, *d.DISH_MSG_PACK, u.check_dish_updated),
    (DELETE, d.ENDPOINT_DISH, d.ID, None, *d.DISH_MSG_PACK, u.check_dish_deleted),
))
async def test_standard(dish, async_client, get_menu_crud, get_submenu_crud, get_dish_crud,
                        method, endpoint, path_param, payload, msg_already_exists, msg_not_found, check_func):
    crud = u.get_crud(endpoint, menu_crud=get_menu_crud, submenu_crud=get_submenu_crud, dish_crud=get_dish_crud)
    assert len(await crud.get_all()) == 1
    await standard_tests(async_client, method, endpoint,
                         path_param=path_param, json=payload,
                         msg_already_exists=msg_already_exists,
                         msg_not_found=msg_not_found,
                         func_check_valid_response=check_func)
    if method == DELETE:
        assert not await crud.get_all()
    else:
        assert len(await crud.get_all()) == 1


async def test_menu_post(async_client, get_menu_crud):
    assert not await get_menu_crud.get_all()
    await standard_tests(async_client, POST, d.ENDPOINT_MENU,
                         json=d.MENU_POST_PAYLOAD,
                         msg_already_exists=d.MENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.MENU_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_created_menu)
    assert await get_menu_crud.get_all()


async def test_submenu_post(menu, async_client, get_submenu_crud):
    assert await get_submenu_crud.get_all() is None
    await standard_tests(async_client, POST, d.ENDPOINT_SUBMENU,
                         json=d.SUBMENU_POST_PAYLOAD,
                         msg_already_exists=d.SUBMENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.SUBMENU_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_created_submenu)
    assert await get_submenu_crud.get_all() is not None


async def test_dish_post(submenu, async_client, get_dish_crud):
    assert await get_dish_crud.get_all() is None
    await standard_tests(async_client, POST, d.ENDPOINT_DISH,
                         json=d.DISH_POST_PAYLOAD,
                         msg_already_exists=d.DISH_ALREADY_EXISTS_MSG,
                         msg_not_found=d.DISH_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_dish)
    assert await get_dish_crud.get_all() is not None
