from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api.endpoints import utils as u
from app.core import get_async_session, settings
from app.services import menu_service
from app.tasks import task

router = APIRouter(prefix=f'{settings.URL_PREFIX}menus', tags=['Menus'])

NAME = 'меню'
SUM_ALL_ITEMS = u.SUM_ALL_ITEMS.format(NAME)
SUM_ITEM = u.SUM_ITEM.format(NAME)
SUM_CREATE_ITEM = u.SUM_CREATE_ITEM.format(NAME)
SUM_UPDATE_ITEM = u.SUM_UPDATE_ITEM.format(NAME)
SUM_DELETE_ITEM = u.SUM_DELETE_ITEM.format(NAME)
SUM_FULL_LIST = f'Полный список {NAME}.'


@router.get(
    '',
    response_model=list[schemas.MenuOut],
    summary=SUM_ALL_ITEMS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_ITEMS}'))
async def get_all_(menu_service: menu_service):
    menus = await menu_service.get_all()
    return [] if menus is None else menus


@router.get(
    '-full-list',
    response_model=list[dict],
    summary=SUM_FULL_LIST,
    description=(f'{settings.SUPER_ONLY} {SUM_FULL_LIST}'))
async def get_full_list(menu_service: menu_service):
    menus = await menu_service.get_all()
    return [] if menus is None else [jsonable_encoder(m) for m in menus]


@router.post(
    '',
    status_code=201,
    response_model=schemas.MenuOut,
    summary=SUM_CREATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_ITEM}'))
async def create_(payload: schemas.MenuIn, menu_service: menu_service):
    return await menu_service.create(payload)


@router.get(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_ITEM,
    description=(f'{settings.ALL_USERS} {SUM_ITEM}'))
async def get_(item_id: int, menu_service: menu_service):
    return await menu_service.get_or_404(item_id)


@router.patch(
    '/{item_id}',
    response_model=schemas.MenuOut,
    summary=SUM_UPDATE_ITEM,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_ITEM}'))
async def update_(item_id: int, payload: schemas.MenuIn, menu_service: menu_service):
    return await menu_service.update(item_id, payload)


@router.delete(
    '/{item_id}',
    summary=SUM_DELETE_ITEM,
    description=(f'{settings.SUPER_ONLY} {SUM_DELETE_ITEM}'))
async def delete_(item_id: int, menu_service: menu_service):
    await menu_service.delete(item_id)
    return u.delete_response('menu')


@router.get('_synchronize', include_in_schema=False)
async def synchronize(session: AsyncSession = Depends(get_async_session)):
    return await task(session)


'''
@router.get(
    '-full-list',
    response_model=list[dict],
    summary=SUM_FULL_LIST,
    description=(f'{settings.SUPER_ONLY} {SUM_FULL_LIST}'))
async def get_full_list(menu_service: menu_service,
                        background_tasks: BackgroundTasks):
    return [jsonable_encoder(m) for m in
            await get_all_(menu_service, background_tasks)]

'''
