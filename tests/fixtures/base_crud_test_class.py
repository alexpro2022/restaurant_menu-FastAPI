from http import HTTPStatus

import pytest
from fastapi import HTTPException


class CrudAbstractTestClass:
    """Абстрактный класс для тестирования базового CRUD класса."""
    model = None
    schema = None
    crud_base = None
    field_names: tuple | None = None
    post_payload: dict | None = None
    update_payload: dict | None = None
    msg_already_exists: str | None = None
    msg_not_found: str | None = None

    def _check_exc_info(self, exc_info, err, msg):
        for index, item in enumerate((err, msg)):
            assert exc_info.value.args[index] == item, (exc_info.value.args[index], item)

    def _check_exc_info_not_found(self, exc_info):
        self._check_exc_info(exc_info, HTTPStatus.NOT_FOUND, self.msg_not_found)

    def _check_obj(self, obj):
        assert isinstance(obj, self.model)
        for field_name in self.field_names:
            assert hasattr(obj, field_name), field_name

    def _compare_obj_payload(self, obj, payload):
        assert obj.title == payload['title'], (obj.title, payload['title'])
        assert obj.description == payload['description'], (obj.description, payload['description'])

    def _get_method(self, instance, method_name):
        method = instance.__getattribute__(method_name)
        assert isinstance(method, type(instance.__init__))
        return method

    def _is_allowed_implemented(self) -> bool:
        try:
            self.crud_base.is_update_allowed(None, None)
            self.crud_base.is_delete_allowed(None)
        except NotImplementedError:
            return False
        return True

    def _is_perform_create_implemented(self) -> bool:
        try:
            self.crud_base.perform_create(None)
        except NotImplementedError:
            return False
        return True

    def _is_perform_update_implemented(self) -> bool:
        try:
            self.crud_base.perform_update(None, None)
        except NotImplementedError:
            return False
        return True

    @pytest.mark.anyio
    async def test_save(self, get_test_session):
        obj = await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        assert obj
        self._check_obj(obj)

    @pytest.mark.anyio
    async def test_save_exception(self, get_test_session):
        with pytest.raises(HTTPException) as exc_info:
            [await self.crud_base._save(get_test_session, self.model(**self.post_payload)) for _ in range(2)]
        self._check_exc_info(exc_info, HTTPStatus.BAD_REQUEST, self.msg_already_exists)

    @pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
    @pytest.mark.anyio
    async def test_not_found_exception(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        args = (get_test_session, 'title', 'invalid_value')
        menu = await method(*args, exception=False)
        assert menu in (None, [])
        with pytest.raises(HTTPException) as exc_info:
            await method(*args, exception=True)
        self._check_exc_info_not_found(exc_info)

    @pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
    @pytest.mark.anyio
    async def test_get_by_(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        # returns None if NOT_FOUND and exception False
        result = await method(get_test_session, 'title', self.post_payload['title'])
        assert result is None
        # raises HTTPException if NOT_FOUND and exception True
        with pytest.raises(HTTPException) as exc_info:
            await method(get_test_session, 'title', self.post_payload['title'], exception=True)
        self._check_exc_info_not_found(exc_info)
        # returns list of objects or object
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        result = await method(get_test_session, 'title', self.post_payload['title'])
        self._check_obj(result) if method_name == 'get_by_attr' else self._check_obj(result[0])

    @pytest.mark.anyio
    async def test_get(self, get_test_session):
        method = self.crud_base.get
        args = (get_test_session, 1)
        obj = await method(*args)
        assert obj is None
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        obj = await method(*args)
        self._check_obj(obj)

    @pytest.mark.anyio
    async def test_get_or_404(self, get_test_session):
        method = self.crud_base.get_or_404
        args = (get_test_session, 1)
        with pytest.raises(HTTPException) as exc_info:
            await method(*args)
        self._check_exc_info_not_found(exc_info)
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        obj = await method(*args)
        self._check_obj(obj)

    @pytest.mark.anyio
    async def test_get_all(self, get_test_session):
        method = self.crud_base.get_all
        objs = await method(get_test_session)
        assert objs is None
        with pytest.raises(HTTPException) as exc_info:
            await method(get_test_session, exception=True)
        self._check_exc_info_not_found(exc_info)
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        objs = await method(get_test_session)
        assert isinstance(objs, list)
        self._check_obj(objs[0])

    @pytest.mark.parametrize('method_name, args, expected_msg', (
        ('has_permission', (None, None), 'has_permission() must be implemented.'),
        ('is_update_allowed', (None, None), 'is_update_allowed() must be implemented.'),
        ('is_delete_allowed', (None,), 'is_delete_allowed() must be implemented.'),
        ('perform_create', (None, None), 'perform_create() must be implemented.'),
        ('perform_update', (None, None), 'perform_update() must be implemented.'),
    ))
    def test_not_implemented_exception(self, method_name, args, expected_msg):
        if self._is_allowed_implemented() and method_name in ('is_update_allowed', 'is_delete_allowed'):
            pytest.skip(reason='is_allowed implemented')
        if self._is_perform_create_implemented() and method_name == 'perform_create':
            pytest.skip(reason='perform_create implemented')
        if self._is_perform_update_implemented() and method_name == 'perform_update':
            pytest.skip(reason='perform_update implemented')
        with pytest.raises(NotImplementedError) as exc_info:
            self._get_method(self.crud_base, method_name)(*args)
        assert exc_info.value.args[0] == expected_msg

    @pytest.mark.anyio
    async def test_create_raises_not_implemeted_exception(self, get_test_session):
        if self._is_perform_create_implemented():
            pytest.skip(reason='perform_create implemented')
        with pytest.raises(NotImplementedError) as exc_info:
            await self.crud_base.create(get_test_session, self.schema(**self.post_payload), perform_create=True)
        assert exc_info.value.args[0] == 'perform_create() must be implemented.'

    @pytest.mark.anyio
    async def test_create_method(self, get_test_session):
        assert await self.crud_base.get_all(get_test_session) is None
        created = await self.crud_base.create(get_test_session, self.schema(**self.post_payload))
        assert len(await self.crud_base.get_all(get_test_session)) == 1
        self._compare_obj_payload(created, self.post_payload)

    @pytest.mark.anyio
    async def test_perform_create_method(self, get_test_session):
        if not self._is_perform_create_implemented():
            pytest.skip(reason='perform_create not implemented')
        assert await self.crud_base.get_all(get_test_session) is None
        created = await self.crud_base.create(get_test_session, self.schema(**self.post_payload), extra_data='extra-data', perform_create=True)
        assert len(await self.crud_base.get_all(get_test_session)) == 1
        assert created.description == self.post_payload['description']
        assert created.title != self.post_payload['title']
        assert created.title == 'extra-data'

    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    @pytest.mark.anyio
    async def test_update_delete_raises_not_found_exceptions(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        with pytest.raises(HTTPException) as exc_info:
            await method(get_test_session, *args)
        self._check_exc_info_not_found(exc_info)

    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    @pytest.mark.anyio
    async def test_update_delete_raises_has_permission_exceptions(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        with pytest.raises(NotImplementedError) as exc_info:
            await method(get_test_session, *args, user=1)
        assert exc_info.value.args[0] == 'has_permission() must be implemented.', exc_info.value.args[0]

    @pytest.mark.parametrize('method_name, expected_msg', (
        ('update', 'is_update_allowed() must be implemented.'),
        ('delete', 'is_delete_allowed() must be implemented.'),
    ))
    @pytest.mark.anyio
    async def test_update_delete_raises_is_allowed_exceptions(self, get_test_session, method_name, expected_msg):
        if self._is_allowed_implemented():
            pytest.skip(reason='is_allowed implemented')
        method = self._get_method(self.crud_base, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        with pytest.raises(NotImplementedError) as exc_info:
            await method(get_test_session, *args)
        assert exc_info.value.args[0] == expected_msg, (exc_info.value.args[0], expected_msg)

    @pytest.mark.anyio
    async def test_delete_method(self, get_test_session):
        if not self._is_allowed_implemented():
            pytest.skip(reason='is_allowed not implemented')
        created = await self.crud_base.create(get_test_session, self.schema(**self.post_payload))
        assert len(await self.crud_base.get_all(get_test_session)) == 1
        await self.crud_base.delete(get_test_session, created.id)
        assert await self.crud_base.get_all(get_test_session) is None

    @pytest.mark.anyio
    async def test_update_method(self, get_test_session):
        if not self._is_allowed_implemented():
            pytest.skip(reason='is_allowed not implemented')
        created = await self.crud_base.create(get_test_session, self.schema(**self.post_payload))
        self._compare_obj_payload(created, self.post_payload)
        updated = await self.crud_base.update(get_test_session, created.id, self.schema(**self.update_payload))
        assert created.id == updated.id
        self._compare_obj_payload(updated, self.update_payload)

    @pytest.mark.anyio
    async def test_perform_update_method(self, get_test_session):
        if not self._is_allowed_implemented():
            pytest.skip(reason='is_allowed not implemented')
        created = await self.crud_base.create(get_test_session, self.schema(**self.post_payload))
        updated = await self.crud_base.update(get_test_session, created.id, self.schema(**self.update_payload.copy()), perform_update=True)
        assert created.id == updated.id
        assert updated.description == self.update_payload['description'], (
            updated.description, self.update_payload['description'])
        assert updated.title != self.update_payload['title'], (updated.title, self.update_payload['title'])
        assert updated.title == 'perform_updated_done'
