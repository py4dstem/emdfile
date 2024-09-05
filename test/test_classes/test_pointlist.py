from emdfile import PointList
from os.path import join,exists
from emdfile import _TESTPATH
from emdfile import save, read
import numpy as np

# Set paths
dirpath = _TESTPATH
testpath = join(dirpath,"test_base_classes.h5")

class TestPointList():

    def setup_method(self):
        """ instantiate a PointList
        """
        dtype = [('x',np.int32),('y',np.float32)]

        pl = PointList(
            data = np.zeros(5,dtype=dtype)
        )
        pl['x'][:] = np.arange(5)
        self.x = pl
        pass

    def test_instantiation(self):
        assert isinstance(self.x, PointList)
        pass

    def test_PointList_readwrite(self):

        # save, read, check
        save(testpath,self.x,mode='o')
        pl2 = read(testpath)
        assert(np.array_equal(pl2.data,self.x.data))

    def test_PointList_addition(self):

        # make a structured array of the same dtype
        dtype = self.x.dtype
        new_data = np.ones(3,dtype=dtype)

        # add, resulting in a new pointlist
        # length should be len(old)+len(new)
        new_pointlist = self.x + new_data
        assert(len(new_pointlist) == 8)

        # the old pointlist should be unmodified
        assert(len(self.x) == 5)

        # alternatively if we call the .add method,
        # the old pointlist is modified
        self.x.add(new_data)
        assert(len(self.x) == 8)

        # or if we perform a new assignment, the old
        # pointlist is modified
        self.x += new_pointlist
        assert(len(self.x) == 16)


    def test_simple_vector_PointList(self):

        # make a PointList with a *non*-structured array
        pl = PointList(
            name = 'test_simple_pointlist',
            data = np.arange(5).astype(np.float32)
        )

        # type check
        assert(isinstance(pl,PointList))
        assert(pl.fields == ('',))
        assert(pl._types == (np.float32,))

        # make data to add
        new_data = np.arange(5,8).astype(np.float32)

        # add, resulting in a new pointlist
        # length should be len(old)+len(new)
        new_pointlist = pl + new_data
        assert(len(new_pointlist) == 8)

        # the old pointlist should be unmodified
        assert(len(pl) == 5)

        # alternatively if we call the .add method,
        # the old pointlist is modified
        pl.add(new_data)
        assert(len(pl) == 8)

        # or if we perform a new assignment, the old
        # pointlist is modified
        pl += new_pointlist
        assert(len(pl) == 16)

