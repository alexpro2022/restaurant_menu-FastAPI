from http import HTTPStatus
from typing import Any

from httpx import AsyncClient, Response

DONE = 'DONE'


def assert_status(response: Response, expected_status_code: int) -> None:
    assert response.status_code == expected_status_code, (
        f'\n   {response.status_code}\n   {response.json()}')


def assert_msg(response: Response, expected_msg: str | None) -> None:
    if expected_msg is not None:
        response_json = response.json()
        assert response_json == {'detail': expected_msg}, f'\n   {response_json} {expected_msg}'


def get_invalid_str() -> tuple[str]:
    return None, '', ' ', '-invalid-'


def get_invalid_int() -> tuple[int]:
    return 0, -1, 10**12


def get_invalid_dict_keys(original: dict) -> tuple[dict]:
    dicts = []
    for key in original:
        for invalid_key in get_invalid_str():
            dd = original.copy()
            value = dd.pop(key)
            dd[invalid_key] = value
            dicts.append(dd)
    return None, *dicts


def get_invalid(item: int | str | dict) -> tuple[int | str | dict]:
    if isinstance(item, int):
        return get_invalid_int()
    if isinstance(item, str):
        return get_invalid_str()
    if isinstance(item, dict):
        return get_invalid_dict_keys(item)


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
            return await client.get(endpoint, params=params,headers=headers)
        case 'DELETE':
            return await client.delete(endpoint, params=params,headers=headers)        
        case 'POST':
            return await client.post(endpoint, params=params,headers=headers, data=data, json=json)
        case 'PUT':
            return await client.put(endpoint, params=params,headers=headers, data=data, json=json)
        case 'PATCH':
            return await client.patch(endpoint, params=params,headers=headers, data=data, json=json)
    

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
    response: Response = await get_response(client, method, endpoint, path_param=path_param, params=params, data=data, json=json, headers=headers)
    if expected_status_code is None:
        match method.upper():
            case 'POST':
                expected_status_code = HTTPStatus.CREATED
            case 'DELETE':
                expected_status_code = HTTPStatus.OK
            case _:
                expected_status_code = HTTPStatus.OK
    assert response.status_code == expected_status_code, (response.status_code, expected_status_code, response.headers)
    return response


def __dummy_func(*args, **kwargs) -> str:
    return DONE


async def standard_tests(
    client: AsyncClient,
    method: str,
    endpoint: str,
    *,
    path_param: int | str | None = None,
    params: dict[str, str] | None = None,
    check_params: bool = True,
    json: dict[str, str] | None = None,
    check_json: bool = True,
    data: dict[str, str] | None = None,
    check_data: bool = True,
    headers: dict | None = None,
    func_check_valid_response: Any | None = None,
    msg_already_exists: str | None = None,
    msg_not_found: str | None = None,
) -> None:
    # valid_request_test
    response = await assert_response(None, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
    match method.upper():
        # Sequential POST with the same data should get Integrity Error which raises BAD_REQUEST
        case 'POST':
            r = await assert_response(HTTPStatus.BAD_REQUEST, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
            assert_msg(r, msg_already_exists)
        # Sequential DELETE with the same data should get NOT_FOUND
        case 'DELETE':
            r = await assert_response(HTTPStatus.NOT_FOUND, client, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers)
            assert_msg(r, msg_not_found)
    if func_check_valid_response is None:
        func_check_valid_response = __dummy_func
    assert func_check_valid_response(response.json()) == DONE

    # invalid_endpoint_test -----------------------------------------------------------------------------------
    for invalid_endpoint in get_invalid(endpoint):
        await assert_response(HTTPStatus.NOT_FOUND, client, method, invalid_endpoint, path_param=path_param,  params=params, json=json, data=data, headers=headers)

    # invalid_path_param_test -----------------------------------------------------------------------------------
    if path_param is not None:
        for invalid_path_param in get_invalid(path_param):
            r = await assert_response(HTTPStatus.NOT_FOUND, client, method, endpoint,  path_param=invalid_path_param, params=params, json=json, data=data, headers=headers)
            assert_msg(r, msg_not_found)

    # invalid_query_params_keys_test -----------------------------------------------------------------------------------
    if params is not None and check_params:
        for invalid_keys_params in get_invalid(params):
            await assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=invalid_keys_params, json=json, data=data, headers=headers)

    # invalid_payload_keys_test -----------------------------------------------------------------------------------
    if json is not None and check_json:
        for invalid_keys_json in get_invalid(json):
            await assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=params, json=invalid_keys_json, data=data, headers=headers)

    # invalid_form_keys_test -----------------------------------------------------------------------------------
    if data is not None and check_data:
        for invalid_keys_data in get_invalid(data):
            await assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, client, method, endpoint, path_param=path_param, params=params, json=json, data=invalid_keys_data, headers=headers)


async def not_allowed_methods_test(
    client: AsyncClient,       
    not_allowed_methods: tuple[str],
    endpoint: str,
    path_param: int | str | None = None,
) -> None:
    for method in not_allowed_methods:
        await assert_response(HTTPStatus.METHOD_NOT_ALLOWED, client, method, endpoint, path_param=path_param)
