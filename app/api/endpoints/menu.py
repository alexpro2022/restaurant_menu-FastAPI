from typing import Annotated

from fastapi import APIRouter, Depends

from app import schemas, services
from app.core import settings

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Menus'])

menu = Annotated[services.MenuService, Depends()]

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
async def get_all_(crud: menu):
    return await crud.get_all()


@router.post(
    '',
    status_code=201,
    response_model=schemas.MenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(payload: schemas.MenuIn, crud: menu):
    return await crud.create(payload)


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int, crud: menu):
    return await crud.get_or_404(item_id)


@router.patch(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int,
                  payload: schemas.MenuIn,
                  crud: menu):
    return await crud.update(item_id, payload)


@router.delete(
    '/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int, crud: menu):
    return await crud.delete(item_id)
