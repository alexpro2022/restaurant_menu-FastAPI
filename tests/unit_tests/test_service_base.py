import pytest
from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_db_repository import CRUDBaseRepository
from app.repositories.redis_repository import BaseRedis
from app.services.services import BaseService

from ..conftest import pytest_mark_anyio
from ..fixtures import data as d


class TestBaseService:
    model: d.Model
    # session: AsyncSession
    # redis: Redis
    db: CRUDBaseRepository
    redis_db: BaseRedis
    base_service: BaseService

    @pytest.fixture
    def setup_method(self, get_test_session, get_test_redis):
        # self.session = get_test_session
        # self.redis = get_test_redis
        self.db = CRUDBaseRepository(self.model, get_test_session)
        self.redis = BaseRedis(self.redis)
        self.base_service = BaseService(self.db, get_test_redis)
