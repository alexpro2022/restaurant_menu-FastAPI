import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import orm

from .conftest import Dish, Menu, Submenu, TestingSessionLocal

Session = orm.scoped_session(TestingSessionLocal)


class DishFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Dish
        sqlalchemy_session = Session

    title = factory.Sequence(lambda n: 'Title %d' % n)
    description = 
    price = 10.2
    submenu_id =
    submenu =

class SubmenuFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Submenu
        sqlalchemy_session = Session

    title = 
    description =
    menu_id =
    menu =
    dishes =


class MenuFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Menu
        sqlalchemy_session = Session

    title = 
    description =
    submenus =
