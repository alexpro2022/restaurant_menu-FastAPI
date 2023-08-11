from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from app import schemas, services
from app.core import settings

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Menus'])

menu_service = Annotated[services.MenuService, Depends()]

SUM_ALL_ITEMS = 'Выдача списка меню'
SUM_ITEM = 'Возвращает меню по ID'
SUM_CREATE_ITEM = 'Создание нового меню'
SUM_UPDATE_ITEM = 'Редактирование меню'
SUM_DELETE_ITEM = 'Удаление меню'


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
    menu = await menu_service.create(payload)
    background_tasks.add_task(menu_service.set_cache, menu)
    return menu


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int,
               menu_service: menu_service,
               background_tasks: BackgroundTasks):
    menu, cache = await menu_service.get_or_404(item_id)
    if not cache:
        background_tasks.add_task(menu_service.set_cache, menu)
    return menu


@router.patch(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.MenuIn,
                  menu_service: menu_service,
                  background_tasks: BackgroundTasks):
    menu = await menu_service.update(item_id, payload)
    background_tasks.add_task(menu_service.set_cache, menu)
    return menu


@router.delete(
    '/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int,
                  menu_service: menu_service,
                  background_tasks: BackgroundTasks):
    menu = await menu_service.delete(item_id)
    background_tasks.add_task(menu_service.set_cache_delete, menu)
    return {'status': True, 'message': 'The menu has been deleted'}
