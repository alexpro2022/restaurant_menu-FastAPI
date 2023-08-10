import pytest

from app.repositories.db_repository import CRUDRepository, MenuRepository
from tests.fixtures.data import Model
from tests.utils import get_method


class TestCRUDRepository:
    crud: CRUDRepository

    @pytest.fixture
    def init(self, get_test_session):
        self.crud = CRUDRepository(Model, get_test_session)

    @pytest.mark.parametrize('method_name',
                             ('is_update_allowed', 'is_delete_allowed')
                             )
    def test_is_allowed_methods_return_None(self, init, method_name):
        method = get_method(self.crud, method_name)
        assert method() is True


class TestMenuRepository:
    menu_repo_db: MenuRepository

    @pytest.fixture
    def init(self, get_test_session):
        self.menu_repo_db = MenuRepository(get_test_session)
