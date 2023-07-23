from datetime import datetime as dt
from http import HTTPStatus
import pytest

from fastapi import HTTPException

from .conftest import Post, PostCreate, User
from .fixtures.data import POST_PAYLOAD, POST_SAVE_DATA


def _check_exc_info(exc_info, err, msg):
    for index, item in enumerate((err, msg)):
        assert exc_info.value.args[index] == item


def _check_exc_info_not_found(exc_info):
    _check_exc_info(exc_info, HTTPStatus.NOT_FOUND, 'Object(s) not found.')     


def _check(post: Post):
    assert isinstance(post, Post)
    for item in ('title', 'content'):
        assert getattr(post, item) == POST_SAVE_DATA[item]
    assert isinstance(post.created, dt)
    assert post.updated is None
    assert post.likes == 0
    assert post.dislikes == 0


def _get_method(instance, method_name):
    method = instance.__getattribute__(method_name)
    assert isinstance(method, type(instance.__init__))
    return method          


@pytest.mark.anyio
async def test_save(get_crud_base, get_test_session):
    post = await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    _check(post)


@pytest.mark.anyio
async def test_save_exception(get_crud_base, get_test_session):
    with pytest.raises(HTTPException) as exc_info:
        [await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA)) for _ in range(2)]
    _check_exc_info(exc_info, HTTPStatus.BAD_REQUEST, 'Object with such a unique values already exists.')     


@pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
@pytest.mark.anyio
async def test_not_found_exception(get_crud_base, get_test_session, method_name):
    method = _get_method(get_crud_base, method_name)
    args = (get_test_session, 'title', 'title_value')
    post = await method(*args, exception=False)
    assert post in (None, [])
    with pytest.raises(HTTPException) as exc_info:
        await method(*args, exception=True)
    _check_exc_info_not_found(exc_info)  


@pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
@pytest.mark.anyio
async def test_get_by_(get_crud_base, get_test_session, method_name):
    method = _get_method(get_crud_base, method_name)
    await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    result = await method(get_test_session, 'title', POST_SAVE_DATA['title'])
    _check(result) if method_name is 'get_by_attr' else _check(result[0])


@pytest.mark.anyio
async def test_get(get_crud_base, get_test_session):
    method = get_crud_base.get
    args = (get_test_session, 1)
    post = await method(*args)
    assert post is None
    await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    post = await method(*args)
    _check(post)


@pytest.mark.anyio
async def test_get_or_404(get_crud_base, get_test_session):
    method = get_crud_base.get_or_404
    args = (get_test_session, 1)
    with pytest.raises(HTTPException) as exc_info:
        await method(*args)
    _check_exc_info_not_found(exc_info)  
    await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    post = await method(*args)
    _check(post)


@pytest.mark.anyio
async def test_get_all(get_crud_base, get_test_session):
    method = get_crud_base.get_all
    posts = await method(get_test_session)
    assert posts == []
    with pytest.raises(HTTPException) as exc_info:
        await method(get_test_session, exception=True)
    _check_exc_info_not_found(exc_info)  
    await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    posts = await method(get_test_session)
    assert isinstance(posts, list)
    _check(posts[0])


@pytest.mark.parametrize('method_name, args, expected_msg', (
    ('has_permission', (None, None), 'has_permission() must be implemented.'),
    ('is_update_allowed', (None, None), 'is_update_allowed() must be implemented.'),
    ('is_delete_allowed', (None,), 'is_delete_allowed() must be implemented.'),
    ('perform_create', (None, None), 'perform_create() must be implemented.'),
    ('perform_update', (None, None), 'perform_update() must be implemented.'),
))
def test_not_implemented_exception(get_crud_base, method_name, args, expected_msg):
    with pytest.raises(NotImplementedError) as exc_info:
        _get_method(get_crud_base, method_name)(*args)
    assert exc_info.value.args[0] == expected_msg


@pytest.mark.anyio
async def test_create_raises_not_implemeted_exception(get_crud_base, get_test_session):
    with pytest.raises(NotImplementedError) as exc_info:
        await get_crud_base.create(get_test_session, PostCreate(**POST_PAYLOAD))
    assert exc_info.value.args[0] == 'perform_create() must be implemented.'


@pytest.mark.parametrize('method_name, expected_msg, payload', (
    ('update', 'is_update_allowed() must be implemented.', PostCreate(**POST_PAYLOAD)),
    ('delete', 'is_delete_allowed() must be implemented.', None),
))
@pytest.mark.anyio
async def test_func_raises_exceptions(get_crud_base, get_test_session, method_name, expected_msg, payload):
    method = _get_method(get_crud_base, method_name)
    args = (1,) if payload is None else (1, payload) 
    # not found exception
    with pytest.raises(HTTPException) as exc_info:
        await method(get_test_session, *args)
    _check_exc_info_not_found(exc_info)
    # create post for further testing
    await get_crud_base._save(get_test_session, Post(**POST_SAVE_DATA))
    # permissin exception
    with pytest.raises(NotImplementedError) as exc_info:
        await method(get_test_session, *args, user=User)
    assert exc_info.value.args[0] == 'has_permission() must be implemented.'
    # is allowed exception    
    with pytest.raises(NotImplementedError) as exc_info:
        await method(get_test_session, *args)
    assert exc_info.value.args[0] == expected_msg