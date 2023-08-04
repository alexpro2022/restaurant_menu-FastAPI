import pytest

from .fixtures import endpoints_testlib as lib


def test_dummy_func():
    assert lib.__dummy_func() == lib.DONE


def test_getinvalid():
    original = {'first_key': 'first_value',
                'second_key': 'second_value'}
    for invalid in lib.get_invalid(original):
        assert invalid != original
