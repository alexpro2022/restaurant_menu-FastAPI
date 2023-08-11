from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from app import schemas, services
from app.core import settings

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Submenus'])

menu_service = Annotated[services.MenuService, Depends()]
submenu_service = Annotated[services.SubmenuService, Depends()]

SUM_ALL_ITEMS = 'Выдача списка подменю'
SUM_ITEM = 'Возвращает подменю по ID'
SUM_CREATE_ITEM = 'Создание нового подменю'
SUM_UPDATE_ITEM = 'Редактирование подменю'
SUM_DELETE_ITEM = 'Удаление подменю'


@router.get(
    '/{menu_id}/submenus',
    response_model=list[schemas.SubmenuOut],
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(menu_id: int,
                   menu_service: menu_service,
                   submenu_service: submenu_service,
                   background_tasks: BackgroundTasks):
    menu, cache = await menu_service.get(menu_id)  # type: ignore
    if menu is None:
        return []
    if not cache:
        background_tasks.add_task(menu_service.set_cache, menu)
        # background_tasks.add_task(submenu_service.set_cache, menu.submenus)
    return menu.submenus


@router.post(
    '/{menu_id}/submenus',
    status_code=201,
    response_model=schemas.SubmenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(menu_id: int,
                  payload: schemas.SubmenuIn,
                  menu_service: menu_service,
                  submenu_service: submenu_service,
                  background_tasks: BackgroundTasks):
    menu, _ = await menu_service.get_or_404(menu_id)
    submenu = await submenu_service.create(payload, extra_data=menu.id)
    background_tasks.add_task(submenu_service.set_cache_create, submenu)
    return submenu


@router.get(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int,
               submenu_service: submenu_service,
               background_tasks: BackgroundTasks):
    submenu, cache = await submenu_service.get_or_404(item_id)
    if not cache:
        background_tasks.add_task(submenu_service.set_cache, submenu)
    return submenu


@router.patch(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.SubmenuIn,
                  submenu_service: submenu_service,
                  background_tasks: BackgroundTasks):
    submenu = await submenu_service.update(item_id, payload)
    background_tasks.add_task(submenu_service.set_cache, submenu)
    return submenu


@router.delete(
    '/{menu_id}/submenus/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int,
                  submenu_service: submenu_service,
                  background_tasks: BackgroundTasks):
    submenu = await submenu_service.delete(item_id)
    background_tasks.add_task(submenu_service.set_cache_delete, submenu)
    return {'status': True, 'message': 'The submenu has been deleted'}
