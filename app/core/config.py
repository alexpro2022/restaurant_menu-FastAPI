from pydantic import BaseSettings


class Settings(BaseSettings):
    # constants
    DEFAULT_STR = 'To be implemented in .env file'
    SUPER_ONLY = '__Только для суперюзеров:__ '
    AUTH_ONLY = '__Только для авторизованных пользователей:__ '
    ALL_USERS = '__Для всех пользователей:__ '
    URL_PREFIX = '/api/v1/'
    # environment variables
    app_title: str = DEFAULT_STR
    app_description: str = DEFAULT_STR
    secret_key: str = DEFAULT_STR
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    redis_url: str = 'redis://redis:6379'
    redis_expire: int = 3600
    rabbitmq_port: int = 5672
    celery_broker_url: str = f'amqp://guest:guest@rabbitmq:{rabbitmq_port}//'
    celery_task_period: int = 15

    class Config:
        env_file = '.env'


settings = Settings()
