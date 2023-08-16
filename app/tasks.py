from datetime import datetime as dt
from pathlib import Path

import httpx
from celery import Celery
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core import AsyncSessionLocal, db_flush, engine, get_aioredis
from app.schemas import DishIn, MenuIn, SubmenuIn
from app.services import DishService, MenuService, SubmenuService

FILE_PATH = Path('admin/Menu.xlsx')
TIME_INTERVAL = 15.0

celery = Celery('tasks', broker='amqp://guest:guest@rabbitmq:5672')

celery.conf.timezone = 'UTC'


def read_file(fname: str) -> list[dict]:
    wb = load_workbook(filename=fname)
    ws = wb['Лист1']
    menus, submenus, dishes = [], [], []
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
            submenus.append(submenu)
        else:
            dish = {}
            dish['title'] = row[3]
            dish['description'] = row[4]
            dish['price'] = row[5]
            menus[-1]['submenus'][-1]['dishes'].append(dish)
            dishes.append(dish)
    return menus, submenus, dishes


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
    menus, _ = await menu_service.db.get_all()
    await menu_service.set_cache(menus)
    return menus


async def init_repos(fname: Path = FILE_PATH):
    menus, _, _ = read_file(fname)
    if menus:
        await db_flush()
        redis = get_aioredis()
        async with AsyncSessionLocal() as session:
            menu = MenuService(session, redis)
            submenu = SubmenuService(session, redis)
            dish = DishService(session, redis)
            await db_fill(menus, menu, submenu, dish)


async def _task(session, engine: AsyncEngine = engine, fname: Path = FILE_PATH) -> list | None:
    if not is_modified(fname):
        return None
    menus_file, submenus_file, dishes_file = read_file(fname)
    if not menus_file:
        return None
    await init_repos()
    return menus_file


async def _synchronize(session=AsyncSessionLocal):
    async with session() as async_session:
        return await _task(async_session, engine)

client = httpx.Client()


@celery.task(name='celery_worker.synchronize')
def synchronize():
    response = client.get('http://web:8000/api/v1/menus_synchronize')
    return response.json()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(TIME_INTERVAL, synchronize.s(), name='add every 15')
