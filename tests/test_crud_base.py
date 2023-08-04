from typing import Any

from pydantic import BaseModel, Field

from .conftest import Base, CRUDBase
from .fixtures.base_crud_test_class import CrudAbstractTestClass


class Model(Base):
    pass


class Schema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=100)


class CRUD(CRUDBase):

    def is_update_allowed(self, obj: Model | None, payload: dict | None) -> None:
        pass

    def is_delete_allowed(self, obj: Model | None) -> None:
        pass

    def perform_create(self, create_data: dict, extra_data: Any | None = None) -> None:
        if extra_data is not None:
            create_data['title'] = extra_data

    def perform_update(self, obj: Any, update_data: dict) -> Any:
        if obj is None or update_data is None:
            return None
        update_data['title'] = 'perform_updated_done'
        for key, value in update_data.items():
            setattr(obj, key, value)
        return obj


class TestCRUDBaseClass1(CrudAbstractTestClass):
    """Тестовый класс для тестирования базового CRUD класса."""
    model = Model
    schema = Schema
    crud_base = CRUDBase(Model)
    field_names = ('id', 'title', 'description')
    post_payload = {'title': 'My object', 'description': 'My object description'}
    msg_already_exists = 'Object with such a unique values already exists.'
    msg_not_found = 'Object(s) not found.'


class TestCRUDBaseClass2(CrudAbstractTestClass):
    """Тестовый класс для тестирования базового CRUD класса."""
    model = Model
    schema = Schema
    crud_base = CRUD(Model)
    field_names = ('id', 'title', 'description')
    post_payload = {'title': 'My object', 'description': 'My object description'}
    update_payload = {'title': 'My updated object', 'description': 'My updated object description'}
    msg_already_exists = 'Object with such a unique values already exists.'
    msg_not_found = 'Object(s) not found.'
