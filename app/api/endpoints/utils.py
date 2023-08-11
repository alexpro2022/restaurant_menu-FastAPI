from fastapi import BackgroundTasks
from pydantic import BaseModel

from app.services.base import BaseService


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


async def delete_(item_id: int,
                  item_name: str,
                  service: BaseService,
                  background_tasks: BackgroundTasks):
    item = await service.delete(item_id)
    background_tasks.add_task(service.set_cache_delete, item)
    return {'status': True, 'message': f'The {item_name} has been deleted'}
