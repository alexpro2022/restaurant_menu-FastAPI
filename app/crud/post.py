from datetime import datetime as dt
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, User
from app.schemas import PostCreate, PostUpdate

from .base import CRUDBase


class PostCRUD(CRUDBase[Post, PostCreate, PostUpdate]):
    OBJECT_ALREADY_EXISTS = 'Пост с таким заголовком уже существует.'
    NOT_FOUND = 'Пост(ы) не найден(ы).'
    PERMISSION_DENIED = 'У вас нет права доступа к данному посту.'
    SELF_LIKE_DISLIKE_DENIED = (
        'Запрещено ставить LIKE/DISLIKE собственным постам.')

    def __is_admin(self, user: User) -> bool:
        return user.is_superuser

    def perform_create(self, create_data: dict, user: User) -> None:
        """Adds the author to the post record."""
        if user is not None:
            create_data['author_id'] = user.id

    def perform_update(self, obj: Post, update_data: dict) -> Post:
        """Adds the update time and sets updated attributes of the post."""
        update_data['updated'] = dt.now()
        for key in update_data:
            setattr(obj, key, update_data[key])
        return obj

    def has_permission(self, obj: Post, user: User) -> None:
        """Admin or author are only allowed to update/delete the post."""
        if not (self.__is_admin(user) or user.id == obj.author_id):
            raise HTTPException(HTTPStatus.BAD_REQUEST, self.PERMISSION_DENIED)

    def is_delete_allowed(self, obj: Post) -> None:
        """Always allowed in the project."""
        pass

    def is_update_allowed(self, obj: Post, payload: dict) -> None:
        """Always allowed in the project."""
        pass

    async def get_user_posts(
        self, session: AsyncSession, user: User, exception: bool = False
    ) -> list[Post] | None:
        return await self.get_all_by_attr(
            session, 'author_id', user.id, exception=exception)

    async def like_dislike_post(
        self,
        session: AsyncSession,
        post_id: int,
        user: User,
        like: bool = True,
    ) -> Post | None:
        post: Post = await self.get_or_404(session, post_id)
        if post.author_id == user.id:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST, self.SELF_LIKE_DISLIKE_DENIED)
        if like:
            post.likes += 1
        else:
            post.dislikes += 1
        return await self._save(session, post)


post_crud = PostCRUD(Post)
