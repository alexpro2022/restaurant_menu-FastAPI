from fastapi import BackgroundTasks
from pydantic import BaseModel

from app.services.base import BaseService

SUM_ALL_ITEMS = 'Выдача списка {}'
SUM_ITEM = 'Возвращает {} по ID'
SUM_CREATE_ITEM = 'Создание нового {}'
SUM_UPDATE_ITEM = 'Редактирование {}'
SUM_DELETE_ITEM = 'Удаление {}'


async def get_item(item_id: int, service: BaseService, background_tasks: BackgroundTasks):
    item, cache = await service.get_or_404(item_id)
    if not cache:
        background_tasks.add_task(service.set_cache, item)
    return item


async def update(item_id: int,
                 payload: BaseModel,
                 service: BaseService,
                 background_tasks: BackgroundTasks):
    item = await service.update(item_id, payload)
    background_tasks.add_task(service.set_cache, item)
    return item


async def delete(item_id: int,
                 item_name: str,
                 service: BaseService,
                 background_tasks: BackgroundTasks):
    item = await service.delete(item_id)
    background_tasks.add_task(service.set_cache_delete, item)
    return {'status': True, 'message': f'The {item_name} has been deleted'}


async def create(parent_id: int,
                 payload: BaseModel,
                 service: BaseService,
                 background_tasks: BackgroundTasks):
    if parent_id < 0:
        parent_id = None
        method = service.set_cache
    else:
        method = service.set_cache_create
    item = await service.create(payload, extra_data=parent_id)
    background_tasks.add_task(method, item)
    return item


async def get_all(parent_id: int,
                  parent_service: BaseService,
                  service: BaseService,
                  plural_name: str,
                  background_tasks: BackgroundTasks):
    parent, cache = await parent_service.get(parent_id)  # type: ignore
    if parent is None:
        return []
    items = getattr(parent, plural_name)
    if not cache:
        background_tasks.add_task(parent_service.set_cache, parent)
        background_tasks.add_task(service.set_cache, items)
    return items
