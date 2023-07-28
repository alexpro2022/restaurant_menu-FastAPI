from .fixtures import data as d
from .fixtures.endpoints_testlib import DONE


def _check_response(response_json: dict, expected_result: dict):
    assert response_json == expected_result
    return DONE


def check_menu(response_json: dict):
    return _check_response(response_json, d.EXPECTED_MENU)


def check_menu_list(response_json: dict):
    return _check_response(response_json, [d.EXPECTED_MENU])


def check_menu_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_MENU)


def check_menu_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_MENU)


def check_submenu(response_json: dict):
    return _check_response(response_json, d.EXPECTED_SUBMENU)


def check_submenu_list(response_json: dict):
    return _check_response(response_json, [d.EXPECTED_SUBMENU])


def check_submenu_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_SUBMENU)


def check_submenu_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_SUBMENU)


def check_dish(response_json: dict):
    return _check_response(response_json, d.EXPECTED_DISH)


def check_dish_list(response_json: dict):
    return _check_response(response_json, [d.EXPECTED_DISH])


def check_dish_updated(response_json: dict):
    return _check_response(response_json, d.UPDATED_DISH)


def check_dish_deleted(response_json: dict):
    return _check_response(response_json, d.DELETED_DISH)
