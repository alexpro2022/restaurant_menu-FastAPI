import pytest

from .fixtures import data as d
from .fixtures.endpoints_testlib import not_allowed_methods_test, standard_tests
from . import utils as u


@pytest.mark.parametrize('not_allowed_methods, endpoint', (
    (('put',), d.ENDPOINT_DISH),
    (('put',), d.ENDPOINT_MENU),
    (('put',), d.ENDPOINT_SUBMENU),
))
def test_not_allowed_method(not_allowed_methods, endpoint):
    not_allowed_methods_test(not_allowed_methods, endpoint, path_param=d.ID)


@pytest.mark.parametrize('fixture, method, endpoint, path_param, payload, msg_already_exists, msg_not_found, check_func', (
    # -----------------------------------------------------------------------------------------------------------
    ('menu', 'GET', d.ENDPOINT_MENU, None, None, *d.MENU_MSG_PACK, u.check_menu_list),
    ('menu', 'GET', d.ENDPOINT_MENU, d.ID, None, *d.MENU_MSG_PACK, u.check_menu),
    (None, 'POST', d.ENDPOINT_MENU, None, d.MENU_POST_PAYLOAD, *d.MENU_MSG_PACK, u.check_menu),
    ('menu', 'PATCH', d.ENDPOINT_MENU, d.ID, d.MENU_PATCH_PAYLOAD, *d.MENU_MSG_PACK, u.check_menu_updated),
    ('menu', 'DELETE', d.ENDPOINT_MENU, d.ID, None, *d.MENU_MSG_PACK, u.check_menu_deleted),
    # -----------------------------------------------------------------------------------------------------------
    ('submenu', 'GET', d.ENDPOINT_SUBMENU, None, None, *d.SUBMENU_MSG_PACK, u.check_submenu_list),
    ('submenu', 'GET', d.ENDPOINT_SUBMENU, d.ID, None, *d.SUBMENU_MSG_PACK, u.check_submenu),
    ('menu', 'POST', d.ENDPOINT_SUBMENU, None, d.SUBMENU_POST_PAYLOAD, *d.SUBMENU_MSG_PACK, u.check_submenu),
    ('submenu', 'PATCH', d.ENDPOINT_SUBMENU, d.ID, d.SUBMENU_PATCH_PAYLOAD, *d.SUBMENU_MSG_PACK, u.check_submenu_updated),
    ('submenu', 'DELETE', d.ENDPOINT_SUBMENU, d.ID, None, *d.SUBMENU_MSG_PACK, u.check_submenu_deleted),
    # -----------------------------------------------------------------------------------------------------------
    ('dish', 'GET', d.ENDPOINT_DISH, None, None, *d.DISH_MSG_PACK, u.check_dish_list),
    ('dish', 'GET', d.ENDPOINT_DISH, d.ID, None, *d.DISH_MSG_PACK, u.check_dish),
    ('submenu', 'POST', d.ENDPOINT_DISH, None, d.DISH_POST_PAYLOAD, *d.DISH_MSG_PACK, u.check_dish),
    ('dish', 'PATCH', d.ENDPOINT_DISH, d.ID, d.DISH_PATCH_PAYLOAD, *d.DISH_MSG_PACK, u.check_dish_updated),
    ('dish', 'DELETE', d.ENDPOINT_DISH, d.ID, None, *d.DISH_MSG_PACK, u.check_dish_deleted),
))
def test_standard(request, fixture, method, endpoint, path_param, payload, msg_already_exists, msg_not_found, check_func):
    if fixture is not None:
        request.getfixturevalue(fixture)
    standard_tests(method, endpoint, 
                   path_param=path_param,
                   json=payload,
                   msg_already_exists=msg_already_exists,
                   msg_not_found=msg_not_found,
                   func_check_valid_response=check_func)