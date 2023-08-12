from fastapi import APIRouter, BackgroundTasks

from app import schemas
from app.api.endpoints import utils as u
from app.core import settings
from app.services import dish_service, submenu_service

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Dishes'])

NAME = 'блюда'
SUM_ALL_ITEMS = u.SUM_ALL_ITEMS.format('блюд')
SUM_ITEM = u.SUM_ITEM.format('блюдо')
SUM_CREATE_ITEM = u.SUM_CREATE_ITEM.format(NAME)
SUM_UPDATE_ITEM = u.SUM_UPDATE_ITEM.format(NAME)
SUM_DELETE_ITEM = u.SUM_DELETE_ITEM.format(NAME)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[schemas.DishOut] | list,
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(submenu_id: int,
                   submenu_service: submenu_service,
                   dish_service: dish_service,
                   background_tasks: BackgroundTasks):
    return await u.get_all(submenu_id, submenu_service, dish_service, 'dishes', background_tasks)


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.DishOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(submenu_id: int,
                  payload: schemas.DishIn,
                  submenu_service: submenu_service,
                  dish_service: dish_service,
                  background_tasks: BackgroundTasks):
    submenu, _ = await submenu_service.get_or_404(submenu_id)
    return await u.create(submenu.id, payload, dish_service, background_tasks)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int,
               dish_service: dish_service,
               background_tasks: BackgroundTasks):
    return await u.get_item(item_id, dish_service, background_tasks)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.DishIn,
                  dish_service: dish_service,
                  background_tasks: BackgroundTasks):
    return await u.update(item_id, payload, dish_service, background_tasks)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int,
                  dish_service: dish_service,
                  background_tasks: BackgroundTasks):
    return await u.delete(item_id, 'dish', dish_service, background_tasks)
