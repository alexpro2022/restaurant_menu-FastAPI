from http import HTTPStatus

import pytest
from fastapi import HTTPException


@pytest.mark.anyio
class CrudBaseTestClass:
    model = None
    schema = None
    crud_base = None
    field_names: tuple | None = None
    post_payload: dict | None = None
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

    def _get_method(self, instance, method_name):
        method = instance.__getattribute__(method_name)
        assert isinstance(method, type(instance.__init__))
        return method          

    #@pytest.mark.anyio
    async def test_save(self, get_test_session):
        obj = await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        assert obj
        self._check_obj(obj)

    #@pytest.mark.anyio
    async def test_save_exception(self, get_test_session):
        with pytest.raises(HTTPException) as exc_info:
            [await self.crud_base._save(get_test_session, self.model(**self.post_payload)) for _ in range(2)]
        self._check_exc_info(exc_info, HTTPStatus.BAD_REQUEST, self.msg_already_exists)     

    @pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
    #@pytest.mark.anyio
    async def test_not_found_exception(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        args = (get_test_session, 'title', 'invalid_value')
        menu = await method(*args, exception=False)
        assert menu in (None, [])
        with pytest.raises(HTTPException) as exc_info:
            await method(*args, exception=True)
        self._check_exc_info_not_found(exc_info)  

    @pytest.mark.parametrize('method_name', ('get_all_by_attr', 'get_by_attr'))
    #@pytest.mark.anyio
    async def test_get_by_(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        result = await method(get_test_session, 'title', self.post_payload['title'])
        self._check_obj(result) if method_name is 'get_by_attr' else self._check_obj(result[0])

    #@pytest.mark.anyio
    async def test_get(self, get_test_session):
        method = self.crud_base.get
        args = (get_test_session, 1)
        obj = await method(*args)
        assert obj is None
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        obj = await method(*args)
        self._check_obj(obj)

    #@pytest.mark.anyio
    async def test_get_or_404(self, get_test_session):
        method = self.crud_base.get_or_404
        args = (get_test_session, 1)
        with pytest.raises(HTTPException) as exc_info:
            await method(*args)
        self._check_exc_info_not_found(exc_info)  
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))
        obj = await method(*args)
        self._check_obj(obj)

    #@pytest.mark.anyio
    async def test_get_all(self, get_test_session):
        method = self.crud_base.get_all
        objs = await method(get_test_session)
        assert objs == []
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
        with pytest.raises(NotImplementedError) as exc_info:
            self._get_method(self.crud_base, method_name)(*args)
        assert exc_info.value.args[0] == expected_msg

    #@pytest.mark.anyio
    async def test_create_raises_not_implemeted_exception(self, get_test_session):
        with pytest.raises(NotImplementedError) as exc_info:
            await self.crud_base.create(get_test_session, self.schema(**self.post_payload), perform_create=True)
        assert exc_info.value.args[0] == 'perform_create() must be implemented.'

    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    #@pytest.mark.anyio
    async def test_update_delete_raises_not_found_exceptions(self, get_test_session, method_name):
        method = self._get_method(self.crud_base, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        with pytest.raises(HTTPException) as exc_info:
            await method(get_test_session, *args)
        self._check_exc_info_not_found(exc_info)

    @pytest.mark.parametrize('method_name', ('update', 'delete'))
    #@pytest.mark.anyio
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
    #@pytest.mark.anyio
    async def test_update_delete_raises_is_allowed_exceptions(self, get_test_session, method_name, expected_msg):
        method = self._get_method(self.crud_base, method_name)
        args = (1,) if method_name == 'delete' else (1, self.schema(**self.post_payload))
        await self.crud_base._save(get_test_session, self.model(**self.post_payload))  
        with pytest.raises(NotImplementedError) as exc_info:
            await method(get_test_session, *args)
        assert exc_info.value.args[0] == expected_msg, (exc_info.value.args[0], expected_msg)
