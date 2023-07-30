from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
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
    return await crud.get_all(session)


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
    return await crud.create(session, payload)


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.get_or_404(session, item_id)


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
    return await crud.update(session, item_id, payload)


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
