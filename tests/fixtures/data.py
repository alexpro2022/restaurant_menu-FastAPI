# Endpoints
ID = 1
PREFIX = '/api/v1/'
ENDPOINT_MENU = f'{PREFIX}menus'
ENDPOINT_SUBMENU = f'{ENDPOINT_MENU}/{ID}/submenus'
ENDPOINT_DISH = f'{ENDPOINT_SUBMENU}/{ID}/dishes'


# Messages
MENU_NOT_FOUND_MSG = 'menu not found'
MENU_ALREADY_EXISTS_MSG = 'Меню с таким заголовком уже существует.'

SUBMENU_NOT_FOUND_MSG = 'submenu not found'
SUBMENU_ALREADY_EXISTS_MSG = 'Подменю с таким заголовком уже существует.'

DISH_NOT_FOUND_MSG = 'dish not found'
DISH_ALREADY_EXISTS_MSG = 'Блюдо с таким заголовком уже существует.'


# MENU Data
MENU_POST_PAYLOAD = {"title": "My menu 1",
                     "description": "My menu description 1"}
MENU_PATCH_PAYLOAD = {"title": "My updated menu 1",
                      "description": "My updated menu description 1"}
CREATED_MENU = {"id": "1",
                 "title": "My menu 1",
                 "description": "My menu description 1",
                 "submenus_count": 0,
                 "dishes_count": 0}
UPDATED_MENU = {"id": "1",
                "title": "My updated menu 1",
                "description": "My updated menu description 1",
                "submenus_count": 0,
                "dishes_count": 0}
DELETED_MENU = {"status": True, "message": "The menu has been deleted"}
MENU_SAVE_DATA = MENU_POST_PAYLOAD


# SUBMENU Data
SUBMENU_POST_PAYLOAD = {"title": "My submenu 1",
                        "description": "My submenu description 1"}
SUBMENU_PATCH_PAYLOAD = {"title": "My updated submenu 1",
                         "description": "My updated submenu description 1"}
CREATED_SUBMENU = {"id": "1",
                    "title": "My submenu 1",
                    "description": "My submenu description 1",
                    "dishes_count": 0}
UPDATED_SUBMENU = {"id": "1",
                   "title": "My updated submenu 1",
                   "description": "My updated submenu description 1",
                   "dishes_count": 0}
DELETED_SUBMENU = {"status": True,"message": "The submenu has been deleted"}
SUBMENU_SAVE_DATA = SUBMENU_POST_PAYLOAD


# DISH Data
DISH_POST_PAYLOAD = {"title": "My dish 1",
                     "description": "My dish description 1",
                     "price": "12.50"}
DISH_PATCH_PAYLOAD = {"title": "My updated dish 1",
                      "description": "My updated dish description 1",
                      "price": "14.5"}
CREATED_DISH = {"id": "1",
                 "title": "My dish 1",
                 "description": "My dish description 1",
                 "price": "12.5"}
UPDATED_DISH = {"id": "1",
                "title": "My updated dish 1",
                "description": "My updated dish description 1",
                "price": "14.5"}
DELETED_DISH = {"status": True,"message": "The dish has been deleted"}
DISH_SAVE_DATA = DISH_POST_PAYLOAD
