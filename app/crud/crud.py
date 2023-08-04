from app.models import Dish, Menu, Submenu

from .base import CRUDBaseRepository


class CRUDRepository(CRUDBaseRepository):
    # the methods are not in use in the project
    def is_update_allowed(self, obj, payload) -> None:
        pass

    def is_delete_allowed(self, obj) -> None:
        pass


class MenuCRUD(CRUDRepository):
    NOT_FOUND = 'menu not found'
    OBJECT_ALREADY_EXISTS = 'Меню с таким заголовком уже существует.'


class SubmenuCRUD(CRUDRepository):
    NOT_FOUND = 'submenu not found'
    OBJECT_ALREADY_EXISTS = 'Подменю с таким заголовком уже существует.'

    def perform_create(self, create_data: dict, menu_id: int) -> None:
        create_data['menu_id'] = menu_id


class DishCRUD(CRUDRepository):
    NOT_FOUND = 'dish not found'
    OBJECT_ALREADY_EXISTS = 'Блюдо с таким заголовком уже существует.'

    def perform_create(self, create_data: dict, submenu_id: int) -> None:
        create_data['submenu_id'] = submenu_id


dish_crud = DishCRUD(Dish)
menu_crud = MenuCRUD(Menu)
submenu_crud = SubmenuCRUD(Submenu)
