from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

try:
    from app.main import app
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружен объект приложения `app`.'
        'Проверьте и поправьте: он должен быть доступен в модуле `app.main`.')

try:
    from app.core.db import Base, get_async_session
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружены объекты `Base, get_async_session`. '
        'Проверьте и поправьте: они должны быть доступны в модуле '
        '`app.core.db`.')

try:
    from app.core.init_db import create_user
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружен объект `create_user`.'
        'Проверьте и поправьте: он должен быть доступен в модуле '
        '`app.code.init_db`')

try:
    from app.core.user import current_user
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружен объект `current_user`.'
        'Проверьте и поправьте: он должен быть доступен в модуле '
        '`app.code.user`')

try:
    from app.schemas.user import UserCreate  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружена схема создания пользователя UserCreate. '
        'Проверьте и поправьте: она должна быть доступна в модуле '
        '`app.schemas.user`.')

try:
    from app.schemas.post import PostCreate  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружена схема создания пользователя PostCreate. '
        'Проверьте и поправьте: она должна быть доступна в модуле '
        '`app.schemas.post`.')

try:
    from app.models.user import User
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружена модель пользователя User. '
        'Проверьте и поправьте: она должна быть доступна в модуле '
        '`app.models.user`.')

try:
    from app.crud.base import CRUDBase
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `CRUDBase`. Он должен находиться в модуле `app.crud.base`')

try:
    from app.models.post import Post
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `Post`. Он должен находиться в модуле `app.crud.post`')

try:
    from app.crud.post import PostCRUD  # noqa
except (NameError, ImportError):
    raise AssertionError(
        'Не найден объект `PostCRUD`. Он должен находиться в модуле `app.post.base`')

from .utils import create_post

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,
                             connect_args={"check_same_thread": False})

TestingSessionLocal = async_sessionmaker(expire_on_commit=False,
                                         autocommit=False,
                                         autoflush=False,
                                         bind=engine)


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def get_test_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def superuser_client():
    app.dependency_overrides[current_user] = lambda: User(
        id=1,
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    yield
    app.dependency_overrides[current_user] = current_user


@pytest.fixture
def new_post():
    yield create_post()


@pytest.fixture
def get_crud_base() -> CRUDBase:
    yield CRUDBase(Post)