from app.models import Dish, Menu, Submenu

from .base import CRUDBase


class CRUD(CRUDBase):
    # the methods are not in use in the project
    def is_update_allowed(self, obj: Menu, payload: dict) -> None:
        pass

    def is_delete_allowed(self, obj: Menu) -> None:
        pass


class MenuCRUD(CRUD):
    NOT_FOUND = 'menu not found'


class SubmenuCRUD(CRUD):
    NOT_FOUND = 'submenu not found'

    def perform_create(self, create_data: dict, menu_id: int) -> None:
        create_data['menu_id'] = menu_id


class DishCRUD(CRUD):
    NOT_FOUND = 'dish not found'

    def perform_create(self, create_data: dict, submenu_id: int) -> None:
        create_data['submenu_id'] = submenu_id


dish_crud = DishCRUD(Dish)
menu_crud = MenuCRUD(Menu)
submenu_crud = SubmenuCRUD(Submenu)
