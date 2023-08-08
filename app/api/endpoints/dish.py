from typing import Annotated

from fastapi import APIRouter, Depends

from app import models, schemas, services
from app.core import settings

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Dishes'])

dish = Annotated[services.DishService, Depends()]
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
async def get_all_(submenu_id: int, submenu_crud: submenu):
    submenu = await submenu_crud.get(submenu_id)  # type: ignore
    return [] if submenu is None else submenu.dishes  # type: ignore


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.DishOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(
    submenu_id: int,
    payload: schemas.DishIn,
    submenu_crud: submenu,
    crud: dish,
):
    submenu: models.Submenu = await submenu_crud.get_or_404(submenu_id)
    return await crud.create(payload, extra_data=submenu.id)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int, crud: dish):
    return await crud.get_or_404(item_id)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int, payload: schemas.DishIn, crud: dish):
    return await crud.update(item_id, payload)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int, crud: dish):
    return await crud.delete(item_id)
