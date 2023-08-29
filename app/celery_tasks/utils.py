from datetime import datetime as dt
from pathlib import Path
import aioredis
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.core import db_flush, engine, get_aioredis, settings
from app.schemas import DishIn, MenuIn, SubmenuIn
from app.services import DishService, MenuService, SubmenuService


FILE_PATH = Path('admin/Menu.xlsx')
TIME_INTERVAL = settings.celery_task_period


def read_file(fname: str) -> tuple[list[dict]]:
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
    return (dt.now() - mod_time).total_seconds() <= TIME_INTERVAL


async def fill_repos(menus: list[dict],
                     menu_service: MenuService,
                     submenu_service: SubmenuService,
                     dish_service: DishService) -> None:
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
                        await dish_service.db.create(
                            DishIn(title=dish['title'],
                                   description=dish['description'], price=dish['price']), extra_data=created_submenu.id)


async def init_repos(session: AsyncSession,
                     fname: Path = FILE_PATH,
                     engine: AsyncEngine = engine,
                     redis: aioredis.Redis = get_aioredis()) -> None:
    menus, _, _ = read_file(fname)
    if not menus:
        return None
    await redis.flushall()
    await db_flush(engine)
    await fill_repos(menus,
                     MenuService(session, redis, None),
                     SubmenuService(session, redis, None),
                     DishService(session, redis, None))
    return menus
