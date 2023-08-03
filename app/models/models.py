from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


class Menu(Base):
    submenus: Mapped[list['Submenu']] = relationship(
        back_populates='menu',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    @hybrid_property
    def submenus_count(self) -> int:
        return len(self.submenus)

    @hybrid_property
    def dishes_count(self) -> int:
        return sum([submenu.dishes_count for submenu in self.submenus])

    def __repr__(self) -> str:
        return (f'{super().__repr__()}'
                f'submenus_count: {self.submenus_count}\n'
                f'dishes_count: {self.dishes_count}.\n')


class Submenu(Base):
    menu_id: Mapped[int] = mapped_column(ForeignKey('menu.id'))
    menu: Mapped['Menu'] = relationship(back_populates='submenus')
    dishes: Mapped[list['Dish']] = relationship(
        back_populates='submenu',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    @hybrid_property
    def dishes_count(self) -> int:
        return len(self.dishes)

    def __repr__(self) -> str:
        return f'{super().__repr__()}dishes_count: {self.dishes_count}.\n'


class Dish(Base):
    price: Mapped[float] = mapped_column(default=0)
    submenu_id: Mapped[int] = mapped_column(ForeignKey('submenu.id'))
    submenu: Mapped['Submenu'] = relationship(back_populates='dishes')

    def __repr__(self) -> str:
        return f'{super().__repr__()}price: {self.price}.\n'
