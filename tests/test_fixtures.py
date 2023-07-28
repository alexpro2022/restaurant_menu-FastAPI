from .conftest import MenuCRUD


def test_get_crud_base(get_crud_base) -> None:
    assert isinstance(get_crud_base, MenuCRUD)