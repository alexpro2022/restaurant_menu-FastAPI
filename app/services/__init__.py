from typing import Annotated
from fastapi import Depends
from .base import BaseService
from .services import MenuService, SubmenuService, DishService  # noqa

menu_service = Annotated[MenuService, Depends()]
submenu_service = Annotated[SubmenuService, Depends()]
dish_service = Annotated[DishService, Depends()]
