from typing import Any

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import Base, CRUDBaseRepository, pytest_mark_anyio
from ..fixtures import data as d


class CRUD(CRUDBaseRepository):

    def is_update_allowed(self, obj: d.Model | None, payload: dict | None) -> None:
        pass

    def is_delete_allowed(self, obj: d.Model | None) -> None:
        pass

    def perform_create(self, create_data: dict, extra_data: Any | None = None) -> None:
        create_data['title'] = extra_data

    def perform_update(self, obj: Any, update_data: dict) -> Any | None:
        update_data['title'] = 'perform_updated_done'
        for key, value in update_data.items():
            setattr(obj, key, value)
        return obj


class TestCRUDBaseRepository:
    """Тестовый класс для тестирования базового CRUD класса."""
    model = d.Model
    schema = d.Schema
    field_names = ('id', 'title', 'description')
    post_payload = {'title': 'My object', 'description': 'My object description'}
    update_payload = {'title': 'My updated object', 'description': 'My updated object description'}
    msg_already_exists = 'Object with such a unique values already exists.'
    msg_not_found = 'Object(s) not found.'
    # base crud with not implemented middle methods
    crud_base_not_implemented: CRUDBaseRepository
    # base crud with implemented middle methods
    crud_base_implemented: CRUD
    session: AsyncSession

    @pytest.fixture
    def setup_method(self, get_test_session):
        self.session = get_test_session
        self.crud_base_not_implemented = CRUDBaseRepository(self.model, self.session)
        self.crud_base_implemented = CRUD(self.model, self.session)

    def _check_exc_info(self, exc_info, expected_msg: str, expected_error_code: int | None = None) -> None:
        if expected_error_code is None:
            assert exc_info.value.args[0] == expected_msg
        else:
            for index, item in enumerate((expected_error_code, expected_msg)):
                assert exc_info.value.args[index] == item, (exc_info.value.args[index], item)

    def _check_exc_info_not_found(self, exc_info) -> None:
        self._check_exc_info(exc_info, self.msg_not_found, status.HTTP_404_NOT_FOUND)

    def _check_obj(self, obj: Base) -> None:
        assert isinstance(obj, self.model)
        for field_name in self.field_names:
            assert hasattr(obj, field_name), field_name

    def _compare_obj_payload(self, obj: Base, payload: dict[str, str]) -> None:
        assert obj.title == payload['title'], (obj.title, payload['title'])
        assert obj.description == payload['description'], (obj.description, payload['description'])

    def _get_method(self, instance: CRUDBaseRepository, method_name: str):
        method = instance.__getattribute__(method_name)
        assert isinstance(method, type(instance.__init__))  # type: ignore [misc]
        return method

    async def _create_object(self,) -> Base:
        return await self.crud_base_not_implemented._save(self.model(**self.post_payload))

    async def _get_all(self) -> list | None:
        return await self.crud_base_not_implemented.get_all()

    @pytest_mark_anyio
    async def test_save(self, setup_method):
        self._check_obj(await self._create_object())

    @pytest_mark_anyio
    async def test_save_exception(self, setup_method):
        # first time saves object
        await self._create_object()
        # second attempt to save object with the same attrs raises IntegrityError
        with pytest.raises(HTTPException) as exc_info:
            await self._create_object()
        self._check_exc_info(exc_info, self.msg_already_exists, status.HTTP_400_BAD_REQUEST)

    @pytest_mark_anyio
    @pytest.mark.parametrize('method_name', ('_get_all_by_attrs', '_get_by_attrs'))
    async def test_get_by_methods(self, setup_method, method_name):
        method = self._get_method(self.crud_base_not_implemented, method_name)
        # returns None if NOT_FOUND and exception=False by default
        assert await method(title=self.post_payload['title']) is None
        # raises HTTPException if NOT_FOUND and exception=True
        with pytest.raises(HTTPException) as exc_info:
            await method(title=self.post_payload['title'], exception=True)
        self._check_exc_info_not_found(exc_info)
        # returns list of objects or object if FOUND
        await self._create_object()
        result = await method(title=self.post_payload['title'])
        self._check_obj(result) if method_name == '_get_by_attrs' else self._check_obj(result[0])

    @pytest_mark_anyio
    async def test_get(self, setup_method):
        method = self.crud_base_not_implemented.get
        assert await method(1) is None
        await self._create_object()
        self._check_obj(await method(1))

    @pytest_mark_anyio
    async def test_get_or_404(self, setup_method):
        method = self.crud_base_not_implemented.get_or_404
        with pytest.raises(HTTPException) as exc_info:
            await method(1)
        self._check_exc_info_not_found(exc_info)
        await self._create_object()
        self._check_obj(await method(1))

    @pytest_mark_anyio
    async def test_get_all(self, setup_method):
        method = self.crud_base_not_implemented.get_all
        assert await method() is None
        with pytest.raises(HTTPException) as exc_info:
            await method(exception=True)
        self._check_exc_info_not_found(exc_info)
        await self._create_object()
        objs = await method()
        assert isinstance(objs, list)
        self._check_obj(objs[0])

    @pytest.mark.parametrize('method_name, args, expected_msg', (
        ('has_permission', (None, None), 'has_permission() must be implemented.'),
        ('is_update_allowed', (None, None), 'is_update_allowed() must be implemented.'),
        ('is_delete_allowed', (None,), 'is_delete_allowed() must be implemented.'),
        ('perform_create', (None, None), 'perform_create() must be implemented.'),
        ('perform_update', (None, None), 'perform_update() must be implemented.'),
    ))
    def test_not_implemented_exception(self, method_name, args, expected_msg, setup_method):
        with pytest.raises(NotImplementedError) as exc_info:
            self._get_method(self.crud_base_not_implemented, method_name)(*args)
        self._check_exc_info(exc_info, expected_msg)

    @pytest_mark_anyio
    async def test_create_method_raises_not_implemeted_exception(self, setup_method):
        method = self.crud_base_not_implemented.create
        with pytest.raises(NotImplementedError) as exc_info:
            await method(self.schema(**self.post_payload), extra_data='')
        self._check_exc_info(exc_info, 'perform_create() must be implemented.')

    @pytest_mark_anyio
    async def test_create_method(self, setup_method):
        assert await self._get_all() is None
        created = await self.crud_base_not_implemented.create(self.schema(**self.post_payload))
        assert len(await self._get_all()) == 1
        self._compare_obj_payload(created, self.post_payload)

    @pytest_mark_anyio
    async def test_perform_create_method(self, setup_method):
        EXTRA_DATA = 'extra-data'
        assert await self._get_all() is None
        created = await self.crud_base_implemented.create(self.schema(**self.post_payload), extra_data=EXTRA_DATA)
        assert len(await self._get_all()) == 1
        assert created.description == self.post_payload['description']
        assert created.title != self.post_payload['title']
        assert created.title == EXTRA_DATA

    @pytest_mark_anyio
    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    async def test_update_delete_raise_not_found_exceptions(self, setup_method, method_name):
        method = self._get_method(self.crud_base_not_implemented, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        with pytest.raises(HTTPException) as exc_info:
            await method(*args)
        self._check_exc_info_not_found(exc_info)

    @pytest_mark_anyio
    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    async def test_update_delete_raise_has_permission_exceptions(self, setup_method, method_name):
        method = self._get_method(self.crud_base_not_implemented, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        await self._create_object()
        with pytest.raises(NotImplementedError) as exc_info:
            await method(*args, user=1)
        self._check_exc_info(exc_info, 'has_permission() must be implemented.')

    @pytest_mark_anyio
    @pytest.mark.parametrize('method_name, expected_msg', (
        ('update', 'is_update_allowed() must be implemented.'),
        ('delete', 'is_delete_allowed() must be implemented.'),
    ))
    async def test_update_delete_raises_is_allowed_exceptions(self, setup_method, method_name, expected_msg):
        method = self._get_method(self.crud_base_not_implemented, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        await self._create_object()
        with pytest.raises(NotImplementedError) as exc_info:
            await method(*args)
        self._check_exc_info(exc_info, expected_msg)

    @pytest_mark_anyio
    async def test_delete_method(self, setup_method):
        created = await self._create_object()
        assert len(await self._get_all()) == 1
        await self.crud_base_implemented.delete(created.id)
        assert await self._get_all() is None

    @pytest_mark_anyio
    async def test_update_method(self, setup_method):
        obj = await self._create_object()
        self._compare_obj_payload(obj, self.post_payload)
        upd = await self.crud_base_implemented.update(obj.id, self.schema(**self.update_payload))
        self._compare_obj_payload(obj, self.update_payload)

    @pytest_mark_anyio
    async def test_perform_update_method(self, setup_method):
        obj = await self._create_object()
        await self.crud_base_implemented.update(obj.id, self.schema(**self.update_payload.copy()), perform_update=True)
        assert obj.description == self.update_payload['description']
        assert obj.title != self.update_payload['title']
        assert obj.title == 'perform_updated_done'
