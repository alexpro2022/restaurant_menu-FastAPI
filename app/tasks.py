import asyncio
import typing
from datetime import datetime as dt
from pathlib import Path

from celery import Celery
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core import AsyncSessionLocal, db_flush, engine, get_aioredis
from app.repositories import DishRepository, MenuRepository, SubmenuRepository
from app.schemas import DishIn, MenuIn, SubmenuIn
from app.services import DishService, MenuService, SubmenuService

FILE_PATH = Path('admin/Menu.xlsx')
TIME_INTERVAL = 15.0

celery = Celery('tasks', broker='amqp://guest:guest@rabbitmq:5672')

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
                  menu_service: MenuService,
                  submenu_service: SubmenuService,
                  dish_service: DishService):
    for menu in menus:
        created_menu = await menu_service.db.create(MenuIn(title=menu['title'], description=menu['description']))
        submenus = menu.get('submenus')
        if submenus:
            for submenu in submenus:
                created_submenu = await submenu_service.db.create(
                    SubmenuIn(title=submenu['title'], description=submenu['description']), extra_data=created_menu.id)
                dishes = submenu.get('dishes')
                if dishes:
                    for dish in dishes:
                        created_dish = await dish_service.db.create(
                            DishIn(title=dish['title'],
                                   description=dish['description'], price=dish['price']), extra_data=created_submenu.id)
                        await dish_service.redis.set_obj(created_dish)
                await submenu_service.redis.set_obj(created_submenu)
        await menu_service.redis.set_obj(created_menu)
    return await menu_service.redis.get_all()


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


async def init_repos(fname: Path = FILE_PATH):
    menus = read_file(fname)
    if menus:
        await db_flush()
        redis = get_aioredis()
        async with AsyncSessionLocal() as session:
            menu = MenuService(session, redis)
            submenu = SubmenuService(session, redis)
            dish = DishService(session, redis)
            await db_fill(menus, menu, submenu, dish)


async def _task(session, engine: AsyncEngine, fname: Path = FILE_PATH) -> list | None:
    if not is_modified(fname):
        return None
    menu_repo = MenuRepository(session)
    submenu_repo = SubmenuRepository(session)
    dish_repo = DishRepository(session)
    repos = (menu_repo, submenu_repo, dish_repo,)  # noqa
    menus = read_file(fname)

    return menus


async def _synchronize():
    async with AsyncSessionLocal() as async_session:
        return await _task(async_session, engine)


@celery.task(name='celery_worker.synchronize')
def synchronize():
    return asyncio.run(_synchronize())


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(TIME_INTERVAL, synchronize.s(), name='add every 15')
