from emdfile import PointList, save, read
import numpy as np
from pathlib import Path
import tempfile
import pytest


class TestPointList():

    @pytest.fixture
    def testpath(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    @pytest.fixture
    def pointlist(self):
        """Make a PointList"""
        dtype = [('x',np.int32),('y',np.float32)]
        pl = PointList(data = np.zeros(5,dtype=dtype))
        pl['x'][:] = np.arange(5)
        return pl

    def test_instantiation(self):
        dtype = [('x',np.int32),('y',np.float32)]
        pl = PointList(data = np.zeros(5,dtype=dtype))
        pl['x'][:] = np.arange(5)
        assert isinstance(pl, PointList)
        pass

    def test_pointList(self,pointlist,testpath):
        # save, read, check
        save(testpath,pointlist)
        pl2 = read(testpath)
        assert(np.array_equal(pl2.data,pointlist.data))

    def test_PointList_addition(self,pointlist,testpath):
        # make a structured array of the same dtype
        dtype = pointlist.dtype
        new_data = np.ones(3,dtype=dtype)
        # add, resulting in a new pointlist
        # length should be len(old)+len(new)
        new_pointlist = pointlist + new_data
        assert(len(new_pointlist) == 8)
        # the old pointlist should be unmodified
        assert(len(pointlist) == 5)
        # alternatively if we call the .add method,
        # the old pointlist is modified
        pointlist.add(new_data)
        assert(len(pointlist) == 8)
        # or if we perform a new assignment, the old
        # pointlist is modified
        pointlist += new_pointlist
        assert(len(pointlist) == 16)

    def test_simple_vector_PointList(self):
        # make a PointList with a *non*-structured array
        pl = PointList(
            name = 'test_simple_pointlist',
            data = np.arange(5).astype(np.float32))
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

