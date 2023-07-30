from sqlalchemy import Column, Float, ForeignKey, Integer, orm
from sqlalchemy.ext.hybrid import hybrid_property

from app.core import Base


class Menu(Base):
    submenus = orm.relationship('Submenu',
                                back_populates='menu',
                                cascade='all, delete-orphan',
                                lazy='selectin')

    @hybrid_property
    def submenus_count(self) -> int:
        return len(self.submenus)

    @hybrid_property
    def dishes_count(self) -> int:
        return sum([submenu.dishes_count for submenu in self.submenus])

    def __repr__(self) -> str:
        return (
            f'\nid: {self.id},'
            f'\ntitle: {self.title},'
            f'\ndescription: {self.description},'
        )


class Submenu(Base):
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)
    menu = orm.relationship('Menu', back_populates='submenus')
    dishes = orm.relationship('Dish',
                              back_populates='submenu',
                              cascade='all, delete-orphan',
                              lazy='selectin')

    @hybrid_property
    def dishes_count(self) -> int:
        return len(self.dishes)

    def __repr__(self) -> str:
        return (
            f'\nid: {self.id},'
            f'\ntitle: {self.title},'
            f'\ndescription: {self.description},'
        )


class Dish(Base):
    price = Column(Float, default=0)
    submenu_id = Column(Integer, ForeignKey('submenu.id'), nullable=False)
    submenu = orm.relationship('Submenu', back_populates='dishes')

    def __repr__(self) -> str:
        return (
            f'\nid: {self.id},'
            f'\ntitle: {self.title},'
            f'\ndescription: {self.description},'
            f'\nprice: {self.price}.\n'
        )
