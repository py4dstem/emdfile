from emdfile import Metadata, Node, Root, save, read, _TESTPATH

import numpy as np
from os.path import join, exists
from os import remove

path = join(_TESTPATH, 'test_metadata.h5')



class TestMetadata:

    # setup + teardown

    def setup_method(self):
        """
        Make a simple and a nested Metadata instance.
        Clear filepaths.
        """
        self._clear_data()

        m = Metadata( name='test_metadata' )

        m['x'] = 10
        m['y'] = True
        m['z'] = None
        m['a'] = (1,2,3)
        m['b'] = np.ones((4,5),dtype='uint16')
        m['c'] = (np.ones(5,dtype=bool), np.ones(6,dtype=np.float32))

        n = Metadata( name='test_nested_metadata' )

        n['x'] = 10
        n['y'] = {'arg':1,'barg':(1,2,3),'targ':None}
        n['z'] = {}
        n['z']['a'] = 'moop'
        n['z']['b'] = {}
        n['z']['b']['c'] = True

        self.m = m
        self.n = n
        pass

    def teardown_method(self):
        """
        Clear filepaths.
        """
        self._clear_data()

    def _clear_data(self):
        if exists(path):
            remove(path)
            pass



    # tests

    def test_metadata_basic_io(self):
        """
        Make a metadata instance
        store a piece of data
        save, read
        """
        m = self.m
        save(path, m)
        _m = read(path)

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


    def test_metadata_nested_io(self):
        """
        Make a metadata instance
        store some nested metadata
        save, read
        """
        n = self.n
        save(path, n)
        _n = read(path)

        assert(n['x'] == _n['x'])
        assert(n['y'] == _n['y'])
        assert(n['z'] == _n['z'])
        pass


    def test_empty_lists_and_tups(self):
        """
        """
        m = Metadata( name='metadata' )
        m['x'] = ()
        m['y'] = []
        save(path, m)
        n = read(path)
        assert(n['x'] == ())
        assert(n['y'] == [])




