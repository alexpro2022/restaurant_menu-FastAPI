from openpyxl import load_workbook

from app.tasks import _task, db_fill, read_file
from tests.conftest import FILE_PATH
from tests.conftest import engine as test_engine
from tests.conftest import pytest_mark_anyio
from tests.fixtures import data as d


def info(item):
    print(item)
    assert False


def write_file(fname: str, edit: bool = False) -> None:
    wb = load_workbook(filename=fname)
    ws = wb['Лист1']
    if edit:
        ws['B1'] = 'Menu'
    else:
        ws['B1'] = 'Меню'
    wb.save(filename=fname)


def test_menu_file_exists():
    assert FILE_PATH.exists(), f'No such file: {FILE_PATH}'


def test_read_file():
    assert read_file(FILE_PATH) == d.EXPECTED_MENU_FILE_CONTENT


@pytest_mark_anyio
async def test_db_fill(get_menu_crud, get_submenu_crud, get_dish_crud):
    assert await get_menu_crud.get_all() is None
    menus = read_file(FILE_PATH)
    await db_fill(menus, get_menu_crud, get_submenu_crud, get_dish_crud)
    menus = await get_menu_crud.get_all()
    assert menus is not None
    assert len(menus) == 2
    submenus = await get_submenu_crud.get_all()
    assert submenus is not None
    assert len(submenus) == 4
    dishes = await get_dish_crud.get_all()
    assert dishes is not None
    assert len(dishes) == 12


'''
@pytest_mark_anyio
async def test_task(get_test_session, get_menu_crud):
    assert await _task(get_test_session, test_engine) is None
    write_file(FILE_PATH)
    assert await get_menu_crud.get_all() is None
    assert await _task(get_test_session, test_engine) == d.EXPECTED_MENU_FILE_CONTENT
    assert await get_menu_crud.get_all() is not None
    write_file(FILE_PATH, edit=True)
    new_menus = await _task(get_test_session, test_engine)
    write_file(FILE_PATH)
'''
