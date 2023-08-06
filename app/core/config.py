from pydantic import BaseSettings  # , EmailStr


class Settings(BaseSettings):
    # constants
    DEFAULT_STR = 'To be implemented in .env file'
    DEFAULT_DB_URL = 'sqlite+aiosqlite:///./fastapi.db'
    SUPER_ONLY = '__Только для суперюзеров:__ '
    AUTH_ONLY = '__Только для авторизованных пользователей:__ '
    ALL_USERS = '__Для всех пользователей:__ '
    URL_PREFIX = '/api/v1/'
    # environment variables
    app_title: str = DEFAULT_STR
    app_description: str = DEFAULT_STR
    secret_key: str = DEFAULT_STR
    database_url: str = DEFAULT_DB_URL
    redis_expire: int = 3600

    class Config:
        env_file = '.env'


settings = Settings()
