from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    # constants
    DEFAULT_STR = 'To be implemented in .env file'
    DEFAULT_DB_URL = 'sqlite+aiosqlite:///./fastapi.db'
    SUPER_ONLY = '__Только для суперюзеров:__ '
    AUTH_ONLY = '__Только для авторизованных пользователей:__ '
    ALL_USERS = '__Для всех пользователей:__ '
    # environment variables
    app_title: str = DEFAULT_STR
    app_description: str = DEFAULT_STR
    secret_key: str = DEFAULT_STR
    database_url: str = DEFAULT_DB_URL
    token_lifetime: int = 3600
    token_url: str = 'auth/jwt/login'
    auth_backend_name = 'jwt'
    password_length = 3
    admin_email: EmailStr | None = None
    admin_password: str | None = None

    class Config:
        env_file = '.env'


settings = Settings()
