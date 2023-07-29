import pytest

from . import utils as u
from .fixtures import data as d
from .fixtures.endpoints_testlib import (not_allowed_methods_test,
                                         standard_tests)

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize('not_allowed_methods, endpoint', (
    (('put',), d.ENDPOINT_DISH),
    (('put',), d.ENDPOINT_MENU),
    (('put',), d.ENDPOINT_SUBMENU),
))
async def test_not_allowed_method(not_allowed_methods, endpoint, async_client):
    await not_allowed_methods_test(async_client, not_allowed_methods, endpoint)


async def test_menu_post(async_client, get_menu_crud, get_test_session):
    assert await get_menu_crud.get_all(get_test_session) == []
    await standard_tests(async_client, 'post', d.ENDPOINT_MENU,
                         json=d.MENU_POST_PAYLOAD,
                         msg_already_exists=d.MENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.MENU_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_menu)
    assert await get_menu_crud.get_all(get_test_session) != []


@pytest.mark.parametrize('method, path_param, payload, check_func', (
    ('GET', None, None, u.check_menu_list),
    ('GET',d.ID, None, u.check_menu),
    ('PATCH', d.ID, d.MENU_PATCH_PAYLOAD, u.check_menu_updated),
    ('DELETE', d.ID, None, u.check_menu_deleted),
))
async def test_menu_standard(menu, get_menu_crud, get_test_session, async_client, method, path_param, payload, check_func):
    assert await get_menu_crud.get_all(get_test_session) != []
    await standard_tests(async_client, method, d.ENDPOINT_MENU,
                         path_param=path_param, json=payload,
                         msg_already_exists=d.MENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.MENU_NOT_FOUND_MSG,
                         func_check_valid_response=check_func)
    if method == 'DELETE':
        assert await get_menu_crud.get_all(get_test_session) == []
    else:
        assert await get_menu_crud.get_all(get_test_session) != []


async def test_submenu_post(menu, async_client, get_submenu_crud, get_test_session,):
    assert await get_submenu_crud.get_all(get_test_session) == []
    await standard_tests(async_client, 'post', d.ENDPOINT_SUBMENU,
                         json=d.SUBMENU_POST_PAYLOAD,
                         msg_already_exists=d.SUBMENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.SUBMENU_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_submenu)
    assert await get_submenu_crud.get_all(get_test_session) != []
   


@pytest.mark.parametrize('method, path_param, payload, check_func', (
    ('GET', None, None, u.check_submenu_list),
    ('GET',d.ID, None, u.check_submenu),
    ('PATCH', d.ID, d.SUBMENU_PATCH_PAYLOAD, u.check_submenu_updated),
    ('DELETE', d.ID, None, u.check_submenu_deleted),
))
async def test_submenu_standard(submenu, async_client, get_submenu_crud, get_test_session,method, path_param, payload, check_func):
    assert await get_submenu_crud.get_all(get_test_session) != []
    await standard_tests(async_client, method, d.ENDPOINT_SUBMENU,
                         path_param=path_param, json=payload,
                         msg_already_exists=d.SUBMENU_ALREADY_EXISTS_MSG,
                         msg_not_found=d.SUBMENU_NOT_FOUND_MSG,
                         func_check_valid_response=check_func)
    if method == 'DELETE':
        assert await get_submenu_crud.get_all(get_test_session) == []
    else:
        assert await get_submenu_crud.get_all(get_test_session) != []    


async def test_dish_post(submenu, async_client, get_dish_crud, get_test_session):
    assert await get_dish_crud.get_all(get_test_session) == []
    await standard_tests(async_client, 'post', d.ENDPOINT_DISH,
                         json=d.DISH_POST_PAYLOAD,
                         msg_already_exists=d.DISH_ALREADY_EXISTS_MSG,
                         msg_not_found=d.DISH_NOT_FOUND_MSG,
                         func_check_valid_response=u.check_dish)
    assert await get_dish_crud.get_all(get_test_session) != []


@pytest.mark.parametrize('method, path_param, payload, check_func', (
    ('GET', None, None, u.check_dish_list),
    ('GET',d.ID, None, u.check_dish),
    ('PATCH', d.ID, d.DISH_PATCH_PAYLOAD, u.check_dish_updated),
    ('DELETE', d.ID, None, u.check_dish_deleted),
))
async def test_dish_standard(dish, async_client, get_dish_crud, get_test_session, method, path_param, payload, check_func):
    assert await get_dish_crud.get_all(get_test_session) != []
    await standard_tests(async_client, method, d.ENDPOINT_DISH,
                         path_param=path_param, json=payload,
                         msg_already_exists=d.DISH_ALREADY_EXISTS_MSG,
                         msg_not_found=d.DISH_NOT_FOUND_MSG,
                         func_check_valid_response=check_func)
    if method == 'DELETE':
        assert await get_dish_crud.get_all(get_test_session) == []
    else:
        assert await get_dish_crud.get_all(get_test_session) != []