import typing

from .fixtures import data as d
from .fixtures.endpoints_testlib import DONE


def _check_response(response_json: dict | list, expected_result: dict | list[dict]):
    assert response_json == expected_result
    return DONE


def check_created_menu(response_json: dict):
    return _check_response(response_json, d.CREATED_MENU)


def check_menu(response_json: list):
    return _check_response(response_json, d.EXPECTED_MENU)


def check_menu_list(response_json: list):
    return _check_response(response_json, [d.EXPECTED_MENU])


def check_menu_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_MENU)


def check_menu_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_MENU)


def check_created_submenu(response_json: dict):
    return _check_response(response_json, d.CREATED_SUBMENU)


def check_submenu(response_json: list):
    return _check_response(response_json, d.EXPECTED_SUBMENU)


def check_submenu_list(response_json: list):
    return _check_response(response_json, [d.EXPECTED_SUBMENU])


def check_submenu_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_SUBMENU)


def check_submenu_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_SUBMENU)


def check_dish(response_json: dict):
    return _check_response(response_json, d.CREATED_DISH)


def check_dish_list(response_json: list):
    return _check_response(response_json, [d.CREATED_DISH])


def check_dish_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_DISH)


def check_dish_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_DISH)


def get_crud(endpoint, *, menu_crud, submenu_crud, dish_crud):
    res = endpoint.split('/')
    if 'dishes' in res:
        return dish_crud
    elif 'submenus' in res:
        return submenu_crud
    return menu_crud


def get_method(instance: typing.Any, method_name: str):
    method = instance.__getattribute__(method_name)
    assert isinstance(method, type(instance.__init__))
    return method
