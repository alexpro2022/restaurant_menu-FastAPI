from fastapi import FastAPI

from app.api import main_router
from app.core import settings
from app.tasks import init_repos

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await init_repos()
