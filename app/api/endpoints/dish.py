from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import get_async_session, settings
from app.crud import dish_crud, submenu_crud

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Dishes'])
crud = dish_crud

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
async def get_all_(
    submenu_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    submenu: models.Submenu = await submenu_crud.get(session, submenu_id)
    return [] if submenu is None else submenu.dishes


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.DishOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(
    submenu_id: int,
    payload: schemas.DishIn,
    session: AsyncSession = Depends(get_async_session),
):
    submenu: models.Submenu = await submenu_crud.get_or_404(session,
                                                            submenu_id)
    return await crud.create(session, payload, extra_data=submenu.id)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.get_or_404(session, item_id)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    response_model=schemas.DishOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(
    item_id: int,
    payload: schemas.DishIn,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update(session, item_id, payload)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await crud.delete(session, item_id)
    return {'status': True, 'message': 'The dish has been deleted'}
