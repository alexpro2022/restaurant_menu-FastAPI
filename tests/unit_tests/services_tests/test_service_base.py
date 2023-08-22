import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.repositories.redis_repository import RedisBaseRepository
from app.services.services import BaseService
from tests import conftest as c
from tests.fixtures import data as d
from tests.utils import CRUD, check_exception_info, compare, get_method

pytestmark = c.pytest_mark_anyio


class TestBaseService:
    model = d.Model
    schema = d.Schema
    base_service: BaseService
    post_payload = {'title': 'My object', 'description': 'My object description'}
    update_payload = {'title': 'My updated object', 'description': 'My updated object description'}

    async def _db_empty(self) -> bool:
        db = self.base_service.db
        assert isinstance(db, CRUD)
        return await db.get_all() is None

    async def _cache_empty(self) -> bool:
        r = self.base_service.redis
        assert isinstance(r, RedisBaseRepository)
        return await r.get_all() is None

    @pytest_asyncio.fixture
    async def init(self, get_test_session: c.AsyncSession, get_test_redis: c.FakeRedis) -> None:
        self.base_service = BaseService(CRUD(self.model, get_test_session),
                                        RedisBaseRepository(get_test_redis))
        assert await self._db_empty()
        assert await self._cache_empty()

    @pytest_asyncio.fixture
    async def get_obj_from_db(self, init) -> d.Model:
        obj = await self.base_service.db._save(self.model(**self.post_payload))
        assert not await self._db_empty()
        assert await self._cache_empty()
        return obj

    async def test_set_cache_obj(self, get_obj_from_db: d.Model) -> None:
        assert await self._cache_empty()
        await self.base_service.set_cache(get_obj_from_db)
        assert not await self._cache_empty()

    async def test_set_cache_objs(self, get_obj_from_db: d.Model) -> None:
        assert await self._cache_empty()
        await self.base_service.set_cache([get_obj_from_db])
        assert not await self._cache_empty()

    async def test_get(self, get_obj_from_db: d.Model) -> None:
        # cache stays intact if obj not found in db
        assert await self._cache_empty()
        assert await self.base_service.get(get_obj_from_db.id + 1) is None
        assert await self._cache_empty()
        # cache's been filled if obj found in db
        obj = await self.base_service.get(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert not await self._cache_empty()

    async def test_get_or_404(self, get_obj_from_db: d.Model) -> None:
        # raises exception if no object is found in db
        with pytest.raises(HTTPException):
            await self.base_service.get_or_404(get_obj_from_db.id + 1)
        # cache's been filled if obj found in db
        obj = await self.base_service.get_or_404(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert not await self._cache_empty()

    async def test_get_all_returns_None(self, init) -> None:
        # cache's been filled if obj found in db
        assert await self._cache_empty()
        assert await self.base_service.get_all() is None
        assert await self._cache_empty()

    async def test_get_all_fills_cache(self, get_obj_from_db) -> None:
        assert await self._cache_empty()
        objs = await self.base_service.get_all()
        assert isinstance(objs, list)
        compare(objs[0], get_obj_from_db)
        assert not await self._cache_empty()

    @pytest.mark.parametrize('method_name', ('set_cache_create', 'set_cache_update', 'set_cache_delete'))
    async def test_set_cache_xxx_raises_exc(self, init, method_name: str) -> None:
        with pytest.raises(NotImplementedError) as exc_info:
            await get_method(self.base_service, method_name)(None)
        check_exception_info(exc_info, "Method or function hasn't been implemented yet.")

    async def test_create_creates_obj_and_raises_exc(self, init) -> None:
        assert await self._db_empty()
        assert await self._cache_empty()
        with pytest.raises(NotImplementedError) as exc_info:
            await self.base_service.create(self.schema(**self.post_payload))
        check_exception_info(exc_info, "Method or function hasn't been implemented yet.")
        assert not await self._db_empty()
        assert await self._cache_empty()

    async def test_update(self, get_obj_from_db: d.Model) -> None:
        assert not await self._db_empty()
        assert await self._cache_empty()
        with pytest.raises(NotImplementedError) as exc_info:
            await self.base_service.update(get_obj_from_db.id, self.schema(**self.update_payload))
        check_exception_info(exc_info, "Method or function hasn't been implemented yet.")
        assert not await self._db_empty()
        assert await self._cache_empty()

    async def test_delete(self, get_obj_from_db: d.Model) -> None:
        assert not await self._db_empty()
        assert await self._cache_empty()
        with pytest.raises(NotImplementedError) as exc_info:
            await self.base_service.delete(get_obj_from_db.id)
        check_exception_info(exc_info, "Method or function hasn't been implemented yet.")
        assert await self._db_empty()
        assert await self._cache_empty()