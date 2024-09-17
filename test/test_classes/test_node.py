from emdfile import Node,save,read
from pathlib import Path
import tempfile
import pytest

class TestNode:

    @pytest.fixture
    def _tempfile(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    def test_instantiation(self):
        x = Node()
        assert(isinstance(x,Node))

    def test_node(self,_tempfile):
        x = Node(name='test_node')
        assert(x.name == 'test_node')
        save(_tempfile,x)
        x2 = read(_tempfile)
        assert(isinstance(x2,Node))
        assert(x2.name == 'test_node')

