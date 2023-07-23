from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import current_user, get_async_session, settings
from app.crud.post import post_crud
from app.models import User

router = APIRouter(prefix='/post', tags=['Posts'])

SUM_ALL_POSTS = 'Возвращает список всех постов.'
SUM_ALL_USER_POSTS = ('Возвращает список всех постов '
                      'выполняющего запрос пользователя.')
SUM_POST = 'Возвращает пост по ID.'
SUM_CREATE_POST = 'Создание нового поста.'
SUM_UPDATE_POST = 'Редактирование поста.'
SUM_DELETE_POST = 'Удаление поста.'
SUM_LIKE_POST = 'Поставить LIKE посту.'
SUM_DISLIKE_POST = 'Поставить DISLIKE посту.'


@router.get(
    '/',
    response_model=list[schemas.PostResponse],
    response_model_exclude_none=True,
    summary=SUM_ALL_POSTS,
    description=(f'{settings.ALL_USERS} {SUM_ALL_POSTS}'))
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    return await post_crud.get_all(session)


@router.post(
    '/',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_CREATE_POST,
    description=(f'{settings.AUTH_ONLY} {SUM_CREATE_POST}'))
async def create_post(
    payload: schemas.PostCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    return await post_crud.create(session, payload, user=user)


@router.get(
    '/{post_id}',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_POST,
    description=(f'{settings.ALL_USERS} {SUM_POST}'))
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await post_crud.get_or_404(session, post_id)


@router.put(
    '/{post_id}',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_UPDATE_POST,
    description=(f'{settings.AUTH_ONLY} {SUM_UPDATE_POST}'))
async def update_post(
    post_id: int,
    payload: schemas.PostUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await post_crud.update(session, post_id, payload, user=user)


@router.delete(
    '/{post_id}',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_DELETE_POST,
    description=(
        f'{settings.SUPER_ONLY} {SUM_DELETE_POST}'))
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await post_crud.delete(session, post_id, user)


@router.get(
    '/like/{post_id}',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_LIKE_POST,
    description=(f'{settings.AUTH_ONLY} {SUM_LIKE_POST}'))
async def like_post_(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await post_crud.like_dislike_post(session, post_id, user)


@router.get(
    '/dislike/{post_id}',
    response_model=schemas.PostResponse,
    response_model_exclude_none=True,
    summary=SUM_DISLIKE_POST,
    description=(f'{settings.AUTH_ONLY} {SUM_DISLIKE_POST}'))
async def dislike_post_(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await post_crud.like_dislike_post(session, post_id, user, False)


@router.get(
    '/my_posts/',
    response_model=list[schemas.PostResponse],
    response_model_exclude_none=True,
    summary=SUM_ALL_USER_POSTS,
    description=(f'{settings.AUTH_ONLY} {SUM_ALL_USER_POSTS}'))
async def get_user_posts_(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await post_crud.get_user_posts(session, user)
