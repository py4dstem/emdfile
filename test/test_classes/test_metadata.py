from emdfile import Metadata, Node, save, read
import numpy as np
from pathlib import Path
import tempfile
import pytest


class TestMetadata:

    @pytest.fixture
    def _tempfile(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    @pytest.fixture
    def metadata1(self):
        """Make a non-nested Metadata instance."""
        m = Metadata( name='test_metadata' )
        m['x'] = 10
        m['y'] = True
        m['z'] = None
        m['a'] = (1,2,3)
        m['b'] = np.ones((4,5),dtype='uint16')
        m['c'] = (np.ones(5,dtype=bool), np.ones(6,dtype=np.float32))
        return m

    @pytest.fixture
    def metadata2(self):
        """Make a nested Metadata instance."""
        n = Metadata( name='test_nested_metadata' )
        n['x'] = 10
        n['y'] = {'arg':1,'barg':(1,2,3),'targ':None}
        n['z'] = {}
        n['z']['a'] = 'moop'
        n['z']['b'] = {}
        n['z']['b']['c'] = True
        return n


    def test_instantiation(self):
        m = Metadata()
        assert(isinstance(m,Metadata))
        pass

    def test_metadata1(self,metadata1,_tempfile):
        """Test non-nested metadata"""
        m = metadata1
        save(_tempfile, m)
        _m = read(_tempfile)
        assert(m['x'] == _m['x'])
        assert(m['y'] == _m['y'])
        assert(m['z'] == _m['z'])
        assert(m['a'] == _m['a'])
        assert(np.array_equal(m['b'], _m['b']))
        assert(np.array_equal(m['c'][0], _m['c'][0]))
        assert(np.array_equal(m['c'][1], _m['c'][1]))
        assert(m['b'].dtype == _m['b'].dtype)
        assert(m['c'][0].dtype == _m['c'][0].dtype)
        assert(m['c'][1].dtype == _m['c'][1].dtype)
        pass

    def test_metadata2(self,metadata2,_tempfile):
        """Test nested metadata"""
        n = metadata2
        save(_tempfile, n)
        _n = read(_tempfile)
        assert(n['x'] == _n['x'])
        assert(n['y'] == _n['y'])
        assert(n['z'] == _n['z'])
        pass

    def test_empty_lists_and_tups(self,_tempfile):
        """Test empty lists & tuples """
        m = Metadata( name='metadata' )
        m['x'] = ()
        m['y'] = []
        save(_tempfile, m)
        n = read(_tempfile)
        assert(n['x'] == ())
        assert(n['y'] == [])


