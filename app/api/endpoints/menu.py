from fastapi import APIRouter, Depends, encoders
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import get_async_session, settings
from app.crud import menu_crud

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Menus'])
crud = menu_crud

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
async def get_all_(session: AsyncSession = Depends(get_async_session)):
    return [get_response(menu)
            for menu in await crud.get_all(session)]


@router.post(
    '',
    status_code=201,
    response_model=schemas.MenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(
    payload: schemas.MenuIn,
    session: AsyncSession = Depends(get_async_session),
):
    menu: models.Menu = await crud.create(session, payload)
    return get_response(menu)


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    menu: models.Menu = await crud.get_or_404(session, item_id)
    return get_response(menu)


@router.patch(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(
    item_id: int,
    payload: schemas.MenuIn,
    session: AsyncSession = Depends(get_async_session),
):
    menu: models.Menu = await crud.update(session, item_id, payload)
    return get_response(menu)


@router.delete(
    '/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await crud.delete(session, item_id)
    return {"status": True, "message": "The menu has been deleted"}


def get_response(menu: models.Menu):
    return schemas.MenuOut(**encoders.jsonable_encoder(menu),
                           submenus_count=menu.get_submenus_count(),
                           dishes_count=menu.get_dishes_count())
