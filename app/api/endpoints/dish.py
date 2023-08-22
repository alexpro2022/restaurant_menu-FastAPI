from fastapi import APIRouter

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
    response_model=list[schemas.DishOut],
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(submenu_id: int, submenu_service: submenu_service):
    submenu = await submenu_service.get(submenu_id)  # type: ignore
    return [] if submenu is None else submenu.dishes  # type: ignore


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.DishOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(submenu_id: int,
                  payload: schemas.DishIn,
                  submenu_service: submenu_service,
                  dish_service: dish_service):
    submenu = await submenu_service.get_or_404(submenu_id)
    return await dish_service.create(payload, extra_data=submenu.id)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int, dish_service: dish_service):
    return await dish_service.get_or_404(item_id)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.DishIn,
                  dish_service: dish_service):
    return await dish_service.update(item_id, payload)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int, dish_service: dish_service):
    await dish_service.delete(item_id)
    return u.delete_response('dish')
