import pytest

from ..fixtures import endpoints_testlib as lib

SLASHLESS = ''  # SLASHLESS'


def test_dummy_func():
    assert lib.__dummy_func() == lib.DONE


def test_get_invalid():
    original = {'first_key': 'first_value',
                'second_key': 'second_value'}
    for invalid in lib.get_invalid(original):
        assert invalid != original


@pytest.mark.parametrize('item, expected_result', (
    ('', ''), ('/', ''), ('//', ''), (f'/{SLASHLESS}/', SLASHLESS), (f'///{SLASHLESS}///', SLASHLESS)
))
def test_strip_slashes(item, expected_result):
    assert lib.strip_slashes(item) == expected_result.lower()


@pytest.mark.parametrize('endpoint', (None, '', ' ', '/', '//', SLASHLESS, f'/{SLASHLESS}/', f'///{SLASHLESS}///'))
@pytest.mark.parametrize('path_param', (None, '', '/', '/1', 1))
def test_create_endpoint(endpoint, path_param):
    path = lib.create_endpoint(endpoint, path_param)
    if len(path):
        assert path[0] == '/'
        assert path[-1] != '/'
    else:
        assert path == ''
