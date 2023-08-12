import typing

from fastapi import status

from tests.conftest import Base, CRUDBaseRepository
from tests.fixtures import data as d
from tests.fixtures.endpoints_testlib import DONE


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


def compare(left: Base, right: Base) -> None:
    assert left and right
    assert left.__table__.columns == right.__table__.columns
    for c in left.__table__.columns:
        assert getattr(left, c.key) == getattr(right, c.key)


def check_exception_info(exc_info, expected_msg: str, expected_error_code: int | None = None) -> None:
    if expected_error_code is None:
        assert exc_info.value.args[0] == expected_msg
    else:
        for index, item in enumerate((expected_error_code, expected_msg)):
            assert exc_info.value.args[index] == item, (exc_info.value.args[index], item)


def check_exception_info_not_found(exc_info, msg_not_found) -> None:
    check_exception_info(exc_info, msg_not_found, status.HTTP_404_NOT_FOUND)


class CRUD(CRUDBaseRepository):

    def is_update_allowed(self, obj: d.Model | None, payload: dict | None) -> None:
        pass

    def is_delete_allowed(self, obj: d.Model | None) -> None:
        pass

    def perform_create(self, create_data: dict, extra_data: typing.Any | None = None) -> None:
        create_data['title'] = extra_data

    def perform_update(self, obj: typing.Any, update_data: dict) -> typing.Any | None:
        update_data['title'] = 'perform_updated_done'
        for key, value in update_data.items():
            setattr(obj, key, value)
        return obj
