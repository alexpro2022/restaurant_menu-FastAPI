from fastapi import APIRouter, BackgroundTasks

from app import schemas
from app.api.endpoints import utils as u
from app.core import settings
from app.services import menu_service, submenu_service

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Submenus'])

NAME = 'подменю'
SUM_ALL_ITEMS = u.SUM_ALL_ITEMS.format(NAME)
SUM_ITEM = u.SUM_ITEM.format(NAME)
SUM_CREATE_ITEM = u.SUM_CREATE_ITEM.format(NAME)
SUM_UPDATE_ITEM = u.SUM_UPDATE_ITEM.format(NAME)
SUM_DELETE_ITEM = u.SUM_DELETE_ITEM.format(NAME)


@router.get(
    '/{menu_id}/submenus',
    response_model=list[schemas.SubmenuOut],
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(menu_id: int,
                   menu_service: menu_service,
                   submenu_service: submenu_service,
                   background_tasks: BackgroundTasks):
    return await u.get_all(menu_id, menu_service, submenu_service, 'submenus', background_tasks)


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
    return await u.create(menu.id, payload, submenu_service, background_tasks)


@router.get(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int,
               submenu_service: submenu_service,
               background_tasks: BackgroundTasks):
    return await u.get_item(item_id, submenu_service, background_tasks)


@router.patch(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.SubmenuIn,
                  submenu_service: submenu_service,
                  background_tasks: BackgroundTasks):
    return await u.update(item_id, payload, submenu_service, background_tasks)


@router.delete(
    '/{menu_id}/submenus/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int,
                  submenu_service: submenu_service,
                  background_tasks: BackgroundTasks):
    return await u.delete(item_id, 'submenu', submenu_service, background_tasks)
