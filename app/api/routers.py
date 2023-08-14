from fastapi import APIRouter

from app.api.endpoints import dish, menu, submenu, synch

main_router = APIRouter()


for router in (
    dish.router,
    menu.router,
    submenu.router,
    synch.router,
):
    main_router.include_router(router)
