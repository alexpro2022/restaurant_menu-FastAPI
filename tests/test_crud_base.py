from pydantic import BaseModel, Field

from .conftest import Base, CRUDBase
from .base_test_classes.base_crud_test_class import CrudBaseTestClass


class Model(Base):
    pass


class Schema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=100)


class TestCrudBaseClass(CrudBaseTestClass):
    model = Model
    schema = Schema
    crud_base = CRUDBase(Model)
    field_names = ('id', 'title', 'description')
    post_payload = {"title": "My object", "description": "My object description"}
    msg_already_exists = 'Object with such a unique values already exists.'
    msg_not_found = 'Object(s) not found.'
