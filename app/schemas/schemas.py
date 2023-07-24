from pydantic import BaseModel, Field

# constants for examples
ID = '602033b3-0462-4de1-a2f8-d8494795e0c0'
TITLE = 'My menu/submenu/dish 1'
DESCRIPTION = 'My menu/submenu/dish description 1'
PRICE = 12.50


class IdMixin(BaseModel):
    id: str = Field(max_length=100, example=ID)

    class Config:
        orm_mode = True


class TitleDescriptionMixin(BaseModel):
    title: str = Field(max_length=100, example=TITLE)
    description: str = Field(max_length=100, example=DESCRIPTION)


class DishIn(TitleDescriptionMixin):
    price: float = Field(example=PRICE)


class DishOut(IdMixin, DishIn):
    price: str


class SubmenuIn(TitleDescriptionMixin):
    pass


class SubmenuOut(IdMixin, SubmenuIn):
    dishes_count: int


class MenuIn(TitleDescriptionMixin):
    pass


class MenuOut(IdMixin, MenuIn):
    submenus_count: int
    dishes_count: int
