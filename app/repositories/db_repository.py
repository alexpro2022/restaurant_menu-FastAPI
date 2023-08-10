from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dish, Menu, Submenu

from .base_db_repository import CRUDBaseRepository


class CRUDRepository(CRUDBaseRepository):
    # the methods are not in use in the project
    def is_update_allowed(self, obj=None, payload=None) -> bool:  # type: ignore [override]
        return True

    def is_delete_allowed(self, obj=None) -> bool:  # type: ignore [override]
        return True


class MenuRepository(CRUDRepository):
    NOT_FOUND = 'menu not found'
    OBJECT_ALREADY_EXISTS = 'Меню с таким заголовком уже существует.'

    def __init__(self, session: AsyncSession):
        super().__init__(Menu, session)


class SubmenuRepository(CRUDRepository):
    NOT_FOUND = 'submenu not found'
    OBJECT_ALREADY_EXISTS = 'Подменю с таким заголовком уже существует.'

    def __init__(self, session: AsyncSession):
        super().__init__(Submenu, session)

    def perform_create(self, create_data: dict, menu_id: int) -> None:  # type: ignore
        create_data['menu_id'] = menu_id


class DishRepository(CRUDRepository):
    NOT_FOUND = 'dish not found'
    OBJECT_ALREADY_EXISTS = 'Блюдо с таким заголовком уже существует.'

    def __init__(self, session: AsyncSession):
        super().__init__(Dish, session)

    def perform_create(self, create_data: dict, submenu_id: int) -> None:  # type: ignore
        create_data['submenu_id'] = submenu_id
