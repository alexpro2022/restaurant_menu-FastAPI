import pytest

from .conftest import Menu, Submenu, Dish
from .fixtures import data as d

COMMON_FIELDS = ('id', 'title', 'description')


@pytest.mark.parametrize('model, attrs', (
    (Dish, (*COMMON_FIELDS, 'price', 'submenu_id', 'submenu')),
    (Submenu, (*COMMON_FIELDS, 'dishes', 'menu_id', 'menu')),
    (Menu, (*COMMON_FIELDS, 'submenus')),
))
def test_model_attr(model, attrs):
    for attr_name in attrs:
        assert getattr(model, attr_name, None) is not None


@pytest.mark.parametrize('model, data, attrs', (
    (Dish, d.DISH_SAVE_DATA, (*COMMON_FIELDS, 'price')),
    (Submenu, d.SUBMENU_SAVE_DATA, (*COMMON_FIELDS,)),
    (Menu, d.MENU_SAVE_DATA, (*COMMON_FIELDS,)),
))
def test_model_repr(model, data, attrs):
    representation = str(model(**data))
    for attr_name in attrs:
        assert representation.find(attr_name) != -1