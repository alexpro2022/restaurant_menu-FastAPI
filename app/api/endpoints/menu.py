from fastapi import APIRouter, BackgroundTasks
from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api.endpoints import utils as u
from app.core import settings
from app.services import menu_service
from app.tasks import _synchronize

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Menus'])

NAME = 'меню'
SUM_ALL_ITEMS = u.SUM_ALL_ITEMS.format(NAME)
SUM_ITEM = u.SUM_ITEM.format(NAME)
SUM_CREATE_ITEM = u.SUM_CREATE_ITEM.format(NAME)
SUM_UPDATE_ITEM = u.SUM_UPDATE_ITEM.format(NAME)
SUM_DELETE_ITEM = u.SUM_DELETE_ITEM.format(NAME)
SUM_FULL_LIST = f'Полный список {NAME}.'


@router.get(
    '',
    response_model=list[schemas.MenuOut],
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(menu_service: menu_service,
                   background_tasks: BackgroundTasks):
    items, cache = await menu_service.get_all()
    if not cache:
        background_tasks.add_task(menu_service.set_cache, items)
    return [] if items is None else items


@router.post(
    '',
    status_code=201,
    response_model=schemas.MenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(payload: schemas.MenuIn,
                  menu_service: menu_service,
                  background_tasks: BackgroundTasks):
    return await u.create(-1, payload, menu_service, background_tasks)


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int,
               menu_service: menu_service,
               background_tasks: BackgroundTasks):
    return await u.get_item(item_id, menu_service, background_tasks)


@router.patch(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.MenuIn,
                  menu_service: menu_service,
                  background_tasks: BackgroundTasks):
    return await u.update(item_id, payload, menu_service, background_tasks)


@router.delete(
    '/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int,
                  menu_service: menu_service,
                  background_tasks: BackgroundTasks):
    return await u.delete(item_id, 'menu', menu_service, background_tasks)


@router.get(
    '-full-list',
    response_model=list[dict],
    summary=SUM_FULL_LIST,
    description=(f'{settings.SUPER_ONLY} {SUM_FULL_LIST}'))
async def get_full_list(menu_service: menu_service,
                        background_tasks: BackgroundTasks):
    return [jsonable_encoder(m) for m in
            await get_all_(menu_service, background_tasks)]


@router.get('-without-celery')
async def synch_no_celery():
    return await _synchronize()
