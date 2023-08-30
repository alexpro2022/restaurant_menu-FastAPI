from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
import asyncio
from app.celery_tasks.celery_app import app as celery
from app.core import AsyncSessionLocal, engine
from app.celery_tasks import utils as u


async def task(session: AsyncSession = AsyncSessionLocal(),
               fname: Path = u.FILE_PATH,
               engine: AsyncEngine = engine,
               redis: u.aioredis.Redis = u.get_aioredis()) -> str | list:
    if not u.is_modified(fname):
        return 'Меню не изменялось. Выход из фоновой задачи...'
    result = await u.init_repos(session, fname, engine, redis)
    await session.close()
    return result


@celery.task
def synchronize():
    return asyncio.get_event_loop().run_until_complete(task())
