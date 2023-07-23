import pytest

from .conftest import Post
from .fixtures.data import POST_SAVE_DATA
from .utils import _info


@pytest.mark.parametrize(
    'attr_name,', ('id', 'title', 'content', 'created', 'updated',
                   'likes', 'dislikes', 'author_id', 'author', '__repr__'))
def test_model_attr(attr_name):
    assert getattr(Post, attr_name, None) is not None



def test_model_repr():
    representation = str(Post(**POST_SAVE_DATA))
    for attr_name in ('title', 'content', 'created', 'updated', 'likes', 'dislikes', 'author'):
        assert representation.find(attr_name) != -1