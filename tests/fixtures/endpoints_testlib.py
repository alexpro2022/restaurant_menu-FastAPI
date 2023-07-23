from http import HTTPStatus
from typing import Any, TypeAlias

from fastapi.testclient import TestClient
from httpx import Response

from app.main import app

from .data import POST_ALREADY_EXISTS_MSG, POST_NOT_FOUND_MSG

client = TestClient(app)

GET = 'GET'
POST = 'POST'
PUT = 'PUT'
PATCH = 'PATCH'
DELETE = 'DELETE'
DONE = 'DONE'

Method: TypeAlias = Response
Methods: TypeAlias = tuple[Method]
PathParam: TypeAlias = int | str | None
QueryParams: TypeAlias = dict[str:str] | None
Payload: TypeAlias = dict[str:str] | None


def assert_status(response: Response, expected_status_code: int) -> None:
    assert response.status_code == expected_status_code, f'\n   {response.status_code}\n   {response.json()}'


def assert_msg(response: Response, expected_msg: str) -> None:
    response_json = response.json()
    assert response_json == {'detail': expected_msg}, f'\n   {response_json}'


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


def create_endpoint(endpoint: str, path_param: PathParam) -> str:
    if endpoint in ('/', '//'):
        if path_param is not None:
            return f'/{strip_slashes(str(path_param))}/'
        return '/'
    if path_param is not None:
        return f'/{strip_slashes(endpoint)}/{strip_slashes(str(path_param))}/'
    return f'/{strip_slashes(endpoint)}/'


def get_method(client: TestClient, method: str) -> Method:
    match method.upper():
        case 'GET':
            return client.get
        case 'POST':
            return client.post
        case 'PUT':
            return client.put
        case 'PATCH':
            return client.patch
        case 'DELETE':
            return client.delete


def get_response(
    method: str,
    endpoint: str,
    *,
    _client: TestClient = client,
    path_param: int | str | None = None,
    params: dict[str:str] | None = None,
    json: dict[str:str] | None = None,
    data: dict | None = None,
    headers: dict | None = None,
) -> Response:
    endpoint = create_endpoint(endpoint, path_param)
    if method.upper() in (PATCH, POST, PUT):
        return get_method(_client, method)(endpoint, params=params,headers=headers, data=data, json=json)
    else:
        return get_method(_client, method)(endpoint, params=params,headers=headers)


def assert_response(
    expected_status_code: int,
    method: str,
    endpoint: str,
    *,
    _client: TestClient = client,
    path_param: int | str | None = None,
    params: dict[str:str] | None = None,
    data: dict | None = None,
    json: dict[str:str] | None = None,
    headers: dict | None = None,
) -> Response:
    response: Response = get_response(method, endpoint, _client=_client, path_param=path_param, params=params, data=data, json=json, headers=headers)
    assert response.status_code == expected_status_code, (
        f'{response.status_code} != {expected_status_code} ->'
        f'\n   {method}({create_endpoint(endpoint, path_param)}\n   {headers}\n   {params}\n   {json}\n   {data})'
        f'\n   {response.json()}\n')
    return response


def __dummy_func(response_json) -> str:
    return DONE


def standard_tests(
    method: str,
    endpoint: str,
    *,
    _client: TestClient = client,
    path_param: int | str | None = None,
    params: dict[str:str] | None = None,
    params_optional: bool = False,
    json: dict[str:str] | None = None,
    json_optional: bool = False,
    data: dict[str:str] | None = None,
    data_optional: bool = False,
    headers: dict | None = None,
    func_check_valid_response: Any | None = None,
    msg_invalid_path_param: str | None = None,
) -> None:

    # valid_request_test
    response = assert_response(HTTPStatus.OK, method, endpoint, path_param=path_param, params=params, json=json, data=data, headers=headers, _client=_client)
    match method.upper():
        # Sequential POST with the same data should get a Integrity Error wich raises BAD_REQUEST
        case 'POST':
            r = assert_response(HTTPStatus.BAD_REQUEST, method, endpoint, path_param=path_param,  _client=_client, params=params, json=json, data=data, headers=headers)
            assert_msg(r, POST_ALREADY_EXISTS_MSG)
        # Sequential DELETE with the same data should get NOT_FOUND
        case 'DELETE':
            r = assert_response(HTTPStatus.NOT_FOUND, method, endpoint, path_param=path_param,  _client=_client, params=params, json=json, data=data, headers=headers)
            assert_msg(r, POST_NOT_FOUND_MSG)
    if func_check_valid_response is None:
        func_check_valid_response = __dummy_func
    assert func_check_valid_response(response.json()) == DONE

    # invalid_endpoint_test
    for invalid_endpoint in get_invalid(endpoint):
        assert_response(HTTPStatus.NOT_FOUND, method, invalid_endpoint, path_param=path_param,  _client=_client, params=params, json=json, data=data, headers=headers)

    # invalid_path_param_test
    if path_param is not None:
        for invalid_path_param in get_invalid(path_param):
            r = assert_response(HTTPStatus.NOT_FOUND, method, endpoint,  _client=_client, path_param=invalid_path_param, params=params, json=json, data=data, headers=headers)
            if msg_invalid_path_param is not None:
                assert_msg(r, msg_invalid_path_param)

    # invalid_query_params_keys_test
    if params is not None and not params_optional:
        for invalid_keys_params in get_invalid(params):
            assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, method, endpoint, path_param=path_param,  _client=_client, params=invalid_keys_params, json=json, data=data, headers=headers)

    # invalid_payload_keys_test
    if json is not None and not json_optional:
        for invalid_keys_json in get_invalid(json):
            assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, method, endpoint, path_param=path_param,  _client=_client, params=params, json=invalid_keys_json, data=data, headers=headers)

    # invalid_form_keys_test
    if data is not None and not data_optional:
        for invalid_keys_data in get_invalid(data):
            assert_response(HTTPStatus.UNPROCESSABLE_ENTITY, method, endpoint, path_param=path_param,  _client=_client, params=params, json=json, data=invalid_keys_data, headers=headers)


def not_allowed_methods_test(
    not_allowed_methods: tuple[str],
    endpoint: str,
    path_param: int | str | None = None,
) -> None:
    for method in not_allowed_methods:
        assert_response(HTTPStatus.METHOD_NOT_ALLOWED, method, endpoint, path_param=path_param)


# === ATHORIZATION ===
def get_registered(user: dict) -> None:
    response = client.post('/auth/register', json=user)
    assert_status(response, HTTPStatus.CREATED)
    auth_user = response.json()
    assert isinstance(auth_user['id'], int)
    assert auth_user['email'] == user['email']
    assert auth_user['is_active'] == True
    assert auth_user['is_superuser'] == False
    assert auth_user['is_verified'] == False


def get_auth_user_token(user: dict | None, registration: bool = True) -> str | None:
    if user is None:
        return None
    if registration:
        get_registered(user)
    user = user.copy()
    user['username'] = user['email']
    response = client.post('/auth/jwt/login', data=user)
    assert_status(response, HTTPStatus.OK)
    token = response.json()['access_token']
    assert isinstance(token, str)
    return token


def get_headers(token: str | None) -> dict[str:str] | None:
    if token is None:
        return None
    return {'Authorization': f'Bearer {token}'}
