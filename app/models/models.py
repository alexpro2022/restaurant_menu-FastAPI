from sqlalchemy import Column, Float, ForeignKey, Integer, orm

from app.core import Base


class Menu(Base):
    submenus = orm.relationship('Submenu',
                                back_populates='menu',
                                cascade='all, delete-orphan',
                                lazy='selectin')

    def get_submenus_count(self) -> int:
        return len(self.submenus)

    def get_dishes_count(self) -> int:
        return sum([submenu.get_dishes_count() for submenu in self.submenus])

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

    def get_dishes_count(self) -> int:
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
