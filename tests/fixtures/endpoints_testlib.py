"""
Тесты для проверки ендпойнтов.
Реализованы стандаптные проверки статус кодов, сообщений и ответных данных
при валидных и не валидных значениях в именах ендпойнтов, параметров пути и
в ключах словарей параметров запроса, тела запроса и данных формы(data).
Проверку валидных и не валидных значений этих словарей необходимо реализовывать отдельно.
"""

from http import HTTPStatus
from typing import Any

from httpx import AsyncClient, Response

DONE = 'DONE'


def __dummy_func(*args, **kwargs) -> str:
    return DONE


def assert_msg(response: Response, expected_msg: str | None) -> None:
    if expected_msg is not None:
        response_json = response.json()
        assert response_json == {'detail': expected_msg}, f'\n   {response_json} {expected_msg}'


def get_invalid(item: int | str | dict) -> tuple[int | str | dict]:
    invalid_str = (None, '', ' ', '-invalid-')
    if isinstance(item, int):
        return 0, -1, 10**12
    if isinstance(item, str):
        return invalid_str
    if isinstance(item, dict):
        dicts = []
        for key in item:
            for invalid_key in invalid_str:
                dd = item.copy()
                value = dd.pop(key)
                dd[invalid_key] = value
                dicts.append(dd)
        return None, *dicts


def strip_slashes(item: str) -> str:
    if item and item[0] == '/':
        item = item[1:]
    if item and item[-1] == '/':
        item = item[:-1]
    return item


def create_endpoint(endpoint: str, path_param: dict[str, str] | None = None) -> str:
    if endpoint in ('/', '//'):
        if path_param is not None:
            return f'/{strip_slashes(str(path_param))}'
        return '/'
    if path_param is not None:
        return f'/{strip_slashes(endpoint)}/{strip_slashes(str(path_param))}'
    return f'/{strip_slashes(endpoint)}'


async def get_response(
    client: AsyncClient,
    method: str,
    endpoint: str,
    *,
    path_param: int | str | None = None,
    params: dict[str, str] | None = None,
    json: dict[str, str] | None = None,
    data: dict | None = None,
    headers: dict | None = None,
) -> Response:
    endpoint = create_endpoint(endpoint, path_param)
    match method.upper():
        case 'GET':
            return await client.get(endpoint, params=params, headers=headers)
        case 'DELETE':
            return await client.delete(endpoint, params=params, headers=headers)
        case 'POST':
            return await client.post(endpoint, params=params, headers=headers, data=data, json=json)
        case 'PUT':
            return await client.put(endpoint, params=params, headers=headers, data=data, json=json)
        case 'PATCH':
            return await client.patch(endpoint, params=params, headers=headers, data=data, json=json)


async def assert_response(
    expected_status_code: int | None,
    client: AsyncClient,
    method: str,
    endpoint: str,
    *,
    path_param: int | str | None = None,
    params: dict[str, str] | None = None,
    data: dict | None = None,
    json: dict[str, str] | None = None,
    headers: dict | None = None,
) -> Response:
    response = await get_response(client, method, endpoint, path_param=path_param, params=params, data=data, json=json, headers=headers)
    if expected_status_code is None:
        match method.upper():
            case 'POST':
                expected_status_code = HTTPStatus.CREATED
            case 'DELETE':
                expected_status_code = HTTPStatus.OK  # why not 204 NO_CONTENT ???
            case _:
                expected_status_code = HTTPStatus.OK
    assert response.status_code == expected_status_code, (response.status_code, expected_status_code, response.headers)
    return response


async def standard_tests(
    client: AsyncClient,
    method: str,
    endpoint: str,
    *,
    chec_uniqueness: bool = True,
    path_param: int | str | None = None,
    params: dict[str, str] | None = None,
    check_params: bool = False,
    json: dict[str, str] | None = None,
    check_json: bool = False,
    data: dict[str, str] | None = None,
    check_data: bool = False,
    headers: dict | None = None,
    func_check_valid_response: Any | None = None,
    msg_already_exists: str | None = None,
    msg_not_found: str | None = None,
) -> None:
    method = method.upper()

    # valid_request_test -----------------------------------------------------------------------------------
    response = await assert_response(
        None, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
    if method == 'POST' and chec_uniqueness:
        # Sequential POST with the same data should get Integrity Error which raises BAD_REQUEST
        r = await assert_response(
            HTTPStatus.BAD_REQUEST, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
        assert_msg(r, msg_already_exists)
    elif method == 'DELETE':
        # Sequential DELETE with the same data should get NOT_FOUND
        r = await assert_response(
            HTTPStatus.NOT_FOUND, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
        assert_msg(r, msg_not_found)
    if func_check_valid_response is None:
        func_check_valid_response = __dummy_func
    assert func_check_valid_response(response.json()) == DONE

    # invalid_endpoint_test -----------------------------------------------------------------------------------
    for invalid_endpoint in get_invalid(endpoint):
        await assert_response(
            HTTPStatus.NOT_FOUND, client, method, invalid_endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)

    # invalid_path_param_test -----------------------------------------------------------------------------------
    if path_param is not None:
        for invalid_path_param in get_invalid(path_param):
            r = await assert_response(
                HTTPStatus.NOT_FOUND, client, method, endpoint, path_param=invalid_path_param, params=params, json=json, data=data, headers=headers)
            assert_msg(r, msg_not_found)

    # invalid_query_params_keys_test -----------------------------------------------------------------------------------
    if params is not None and check_params:
        for invalid_params_keys in get_invalid(params):
            await assert_response(
                HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=invalid_params_keys, json=json, data=data, headers=headers)

    # invalid_payload_keys_test -----------------------------------------------------------------------------------
    if json is not None and check_json:
        for invalid_json_keys in get_invalid(json):
            await assert_response(
                HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=params, json=invalid_json_keys, data=data, headers=headers)

    # invalid_form_keys_test -----------------------------------------------------------------------------------
    if data is not None and check_data:
        for invalid_data_keys in get_invalid(data):
            await assert_response(
                HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=params, json=json, data=invalid_data_keys, headers=headers)


async def not_allowed_methods_test(
    client: AsyncClient,
    not_allowed_methods: tuple[str],
    endpoint: str,
    path_param: int | str | None = None,
) -> None:
    for method in not_allowed_methods:
        await assert_response(HTTPStatus.METHOD_NOT_ALLOWED, client, method, endpoint, path_param=path_param)
