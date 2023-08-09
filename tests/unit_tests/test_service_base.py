from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.base import CRUDBaseRepository
from app.repository.redis import BaseRedis
from app.services.services import BaseService

from ..conftest import pytest_mark_anyio
from ..fixtures import data as d


class TestBaseService:
    model: d.Model
    session: AsyncSession
    redis: Redis
    db: CRUDBaseRepository
    redis_db: BaseRedis
    base_service: BaseService

    def setup_method(self, session, redis):
        self.session = session
        self.redis = redis
        self.db = CRUDBaseRepository(self.model, self.session)
        self.redis_db = BaseRedis(self.redis)
        self.base_service = BaseService(self.db, self.redis_db)
