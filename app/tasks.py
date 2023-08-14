import asyncio
import typing
from datetime import datetime as dt
from pathlib import Path

from celery import Celery
from openpyxl import load_workbook

from app.core import AsyncSessionLocal
from app.repositories import DishRepository, MenuRepository, SubmenuRepository
from app.schemas import DishIn, MenuIn, SubmenuIn

FILE_PATH = Path('admin/Menu.xlsx')
TIME_INTERVAL = 15.0

celery = Celery('tasks', broker='amqp://guest:guest@rabbitmq:5672')

celery.conf.beat_schedule = {
    'add-every-15-seconds': {
        'task': 'tasks.synchronize',
        'schedule': TIME_INTERVAL,
    },
}
celery.conf.timezone = 'UTC'


class Hashes:
    menus_hashes: set | None = None
    submenus_hashes: set | None = None
    dishes_hashes: set | None = None

    def set_hashes(self, menus: list[typing.Any]):
        self.menus_hashes = set()
        self.submenus_hashes = set()
        self.dishes_hashes = set()

        for menu in menus:
            self.menus_hashes.add(hash(str(menu)))
            submenus = menu.get('submenus')
            if submenus:
                for submenu in submenus:
                    self.submenus_hashes.add(hash(str(submenu)))
                    dishes = submenu.get('dishes')
                    if dishes:
                        for dish in dishes:
                            self.dishes_hashes.add(hash(str(dish)))

    def is_new_menu(self, menu):
        return hash(str(menu)) not in self.menus_hashes

    def is_new_submenu(self, submenu):
        return hash(str(submenu)) not in self.submenus_hashes

    def is_new_dish(self, dish):
        return hash(str(dish)) not in self.dishes_hashes


hashes = Hashes()


def read_file(fname: str) -> list[dict]:
    wb = load_workbook(filename=fname)
    ws = wb['Лист1']
    menus = []
    for row in ws.values:
        if row[0] is not None:
            menu = {}
            menu['title'] = row[1]
            menu['description'] = row[2]
            menu['submenus'] = []
            menus.append(menu)
        elif row[1] is not None:
            submenu = {}
            submenu['title'] = row[2]
            submenu['description'] = row[3]
            submenu['dishes'] = []
            menus[-1]['submenus'].append(submenu)
        else:
            dish = {}
            dish['title'] = row[3]
            dish['description'] = row[4]
            dish['price'] = row[5]
            menus[-1]['submenus'][-1]['dishes'].append(dish)
    return menus


def is_modified(fname: str) -> bool:
    mod_time = dt.fromtimestamp(fname.stat().st_mtime)
    return (dt.now() - mod_time).total_seconds() < TIME_INTERVAL


async def db_fill(menus: list[dict],
                  menu_repo: MenuRepository,
                  submenu_repo: SubmenuRepository,
                  dish_repo: DishRepository):
    for menu in menus:
        created_menu = await menu_repo.create(MenuIn(title=menu['title'], description=menu['description']))
        submenus = menu.get('submenus')
        if submenus:
            for submenu in submenus:
                created_submenu = await submenu_repo.create(
                    SubmenuIn(title=submenu['title'], description=submenu['description']), extra_data=created_menu.id)
                dishes = submenu.get('dishes')
                if dishes:
                    for dish in dishes:
                        await dish_repo.create(
                            DishIn(title=dish['title'],
                                   description=dish['description'], price=dish['price']), extra_data=created_submenu.id)


async def create_new_items(new_menus,
                           menu_repo: MenuRepository,
                           submenu_repo: SubmenuRepository,
                           dish_repo: DishRepository):
    # for menu in new_menus:
    pass


async def find_and_update(menus, new_menus,
                          menu_repo: MenuRepository,
                          submenu_repo: SubmenuRepository,
                          dish_repo: DishRepository):
    pass


async def find_and_delete(menus,
                          menu_repo: MenuRepository,
                          submenu_repo: SubmenuRepository,
                          dish_repo: DishRepository):
    pass


async def _task(session) -> list | None:
    menu_repo = MenuRepository(session)
    submenu_repo = SubmenuRepository(session)
    dish_repo = DishRepository(session)
    repos = (menu_repo, submenu_repo, dish_repo,)
    menus = read_file(FILE_PATH)
    if hashes.menus_hashes is None:  # first cicle
        await db_fill(menus, *repos)
        hashes.set_hashes(menus)
    elif not is_modified(FILE_PATH):
        return None
    else:
        new_menus = [menu for menu in menus if hashes.is_new_menu(menu)]
        if not new_menus:
            await find_and_delete(menus, *repos)
        elif len(menus) == len(hashes.menus_hashes):
            await find_and_update(menus, new_menus, *repos)
        else:
            await create_new_items(new_menus, *repos)
        hashes.set_hashes(menus)
        return new_menus
    return menus


async def _synchronize():
    async with AsyncSessionLocal() as async_session:
        return await _task(async_session)


@celery.task
def synchronize():
    return asyncio.run(_synchronize())