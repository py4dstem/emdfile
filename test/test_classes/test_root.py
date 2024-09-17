from emdfile import Root
import pytest

class TestRoot:

    @pytest.fixture
    def root(self):
        return Root(name='test_root')

    def test_instantiation(self,root):
        assert(isinstance(root,Root))
        pass

