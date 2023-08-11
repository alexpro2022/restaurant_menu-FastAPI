from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from app import schemas, services
from app.api.endpoints import utils as u
from app.core import settings

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Dishes'])

dish_service = Annotated[services.DishService, Depends()]
submenu = Annotated[services.SubmenuService, Depends()]

SUM_ALL_ITEMS = 'Выдача списка блюд'
SUM_ITEM = 'Возвращает блюдо по ID'
SUM_CREATE_ITEM = 'Создание нового блюда'
SUM_UPDATE_ITEM = 'Редактирование блюда'
SUM_DELETE_ITEM = 'Удаление блюда'


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[schemas.DishOut] | list,
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(submenu_id: int,
                   submenu_crud: submenu,
                   dish_service: dish_service,
                   background_tasks: BackgroundTasks):
    submenu, cache = await submenu_crud.get(submenu_id)  # type: ignore
    if submenu is None:
        return []
    if not cache:
        background_tasks.add_task(submenu_crud.set_cache, submenu)
        background_tasks.add_task(dish_service.set_cache, submenu.dishes)
    return submenu.dishes


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.DishOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(submenu_id: int,
                  payload: schemas.DishIn,
                  submenu_service: submenu,
                  dish_service: dish_service,
                  background_tasks: BackgroundTasks):
    submenu, _ = await submenu_service.get_or_404(submenu_id)
    dish = await dish_service.create(payload, extra_data=submenu.id)
    background_tasks.add_task(dish_service.set_cache_create, dish)
    return dish


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
    return await u.delete_(item_id, 'dish', dish_service, background_tasks)
