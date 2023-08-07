from typing import Annotated

from fastapi import APIRouter, Depends

from app import schemas
from app.core import settings
from app.repository import MenuRepository, SubmenuRepository

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Submenus'])

menu = Annotated[MenuRepository, Depends()]
submenu = Annotated[SubmenuRepository, Depends()]

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
async def get_all_(menu_id: int, menu_crud: menu):
    menu = await menu_crud.get(menu_id)
    return [] if menu is None else menu.submenus


@router.post(
    '/{menu_id}/submenus',
    status_code=201,
    response_model=schemas.SubmenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(
    menu_id: int, payload: schemas.SubmenuIn, menu_crud: menu, crud: submenu
):
    menu = await menu_crud.get_or_404(menu_id)
    return await crud.create(payload, extra_data=menu.id)


@router.get(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int, crud: submenu):
    return await crud.get_or_404(item_id)


@router.patch(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(
    item_id: int, payload: schemas.SubmenuIn, crud: submenu
):
    return await crud.update(item_id, payload)


@router.delete(
    '/{menu_id}/submenus/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int, crud: submenu):
    return await crud.delete(item_id)
