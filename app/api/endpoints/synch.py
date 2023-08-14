from fastapi import APIRouter

from app.core import settings
from app.tasks import _synchronize, synchronize

router = APIRouter(prefix=f'{settings.URL_PREFIX}synchronize', tags=['Database'])

SUMMARY = 'Активирует процесс синхронизации admin-файла и БД.'


@router.get(
    '',
    summary=SUMMARY,
    description=(f'{settings.ALL_USERS} {SUMMARY}'))
async def synch():
    # session: AsyncSession = Depends(get_async_session)) -> None:
    synchronize.delay()


@router.get(
    '/without-celery',
    summary=SUMMARY,
    description=(f'{settings.ALL_USERS} {SUMMARY}'))
async def synch_no_celery():
    return await _synchronize()
