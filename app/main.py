import aioredis
from fastapi import FastAPI

from app.api import main_router
from app.core import settings
from app.repository import redis_client

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
)

app.include_router(main_router)


@app.on_event('startup')
async def startup_event():
    global redis_client
    redis_client = aioredis.from_url(settings.redis_url,
                                     decode_responses=True)


@app.on_event('shutdown')
async def shutdown_event():
    redis_client.close()
