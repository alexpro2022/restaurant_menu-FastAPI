from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import get_async_session, settings
from app.crud import menu_crud, submenu_crud

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Submenus'])
crud = submenu_crud

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
async def get_all_(
    menu_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    menu: models.Menu = await menu_crud.get(session, menu_id)
    return [] if menu is None else menu.submenus


@router.post(
    '/{menu_id}/submenus',
    status_code=201,
    response_model=schemas.SubmenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(
    menu_id: int,
    payload: schemas.SubmenuIn,
    session: AsyncSession = Depends(get_async_session),
):
    menu: models.Menu = await menu_crud.get_or_404(session, menu_id)
    return await crud.create(
        session, payload, extra_data=menu.id, perform_create=True)


@router.get(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.get_or_404(session, item_id)


@router.patch(
    '/{menu_id}/submenus/{item_id}',
    response_model=schemas.SubmenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(
    item_id: int,
    payload: schemas.SubmenuIn,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update(session, item_id, payload)


@router.delete(
    '/{menu_id}/submenus/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await crud.delete(session, item_id)
    return {"status": True, "message": "The submenu has been deleted"}
