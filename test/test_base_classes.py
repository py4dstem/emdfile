import numpy as np
from emdfile import (
    Node,
    Metadata,
    Array,
    PointList,
    PointListArray
)

from os.path import join,exists
from os import remove
from numpy import array_equal

from emdfile import _TESTPATH
from emdfile import save, read

# Set paths
dirpath = _TESTPATH
testpath = join(dirpath,"test_base_classes.h5")





class TestArray():


    def test_instantiation(self):

        shape = (3,4,5)
        d = np.arange(np.prod(shape)).reshape(shape)

        ar = Array(
            data = d
        )
        assert(isinstance(ar, Array))


    def test_Array_complex_readwrite(self):

        # make array
        d = np.exp(1j*np.linspace(0,2*np.pi)).astype(np.complex64)
        ar = Array(
            data = d
        )

        # save, read, check
        save(testpath,ar,mode='o')
        ar2 = read(testpath)
        assert(array_equal(ar.data,ar2.data))




class TestPointList():


    def setup_method(self):
        """ instantiate a PointList
        """
        dtype = [('x',np.int32),('y',np.float32)]

        pl = PointList(
            data = np.zeros(5,dtype=dtype)
        )
        pl['x'][:] = np.arange(5)
        self.pl = pl
        pass


    def test_instantiation(self):
        assert isinstance(self.pl, PointList)
        pass


    def test_PointList_readwrite(self):

        # save, read, check
        save(testpath,self.pl,mode='o')
        pl2 = read(testpath)
        assert(array_equal(pl2.data,self.pl.data))


    def test_PointList_addition(self):

        # make a structured array of the same dtype
        dtype = self.pl.dtype
        new_data = np.ones(3,dtype=dtype)

        # add, resulting in a new pointlist
        # length should be len(old)+len(new)
        new_pointlist = self.pl + new_data
        assert(len(new_pointlist) == 8)

        # the old pointlist should be unmodified
        assert(len(self.pl) == 5)

        # alternatively if we call the .add method,
        # the old pointlist is modified
        self.pl.add(new_data)
        assert(len(self.pl) == 8)

        # or if we perform a new assignment, the old
        # pointlist is modified
        self.pl += new_pointlist
        assert(len(self.pl) == 16)


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



def test_Node():

    # Root class instances should:
    # - have a name
    # - have a Tree
    # - know how to read/write to/from h5

    root = Node()
    assert(isinstance(root,Node))
    ##;passert(root.name == 'root')
    ##;passert(isinstance(root.tree, Tree))

    # h5io


def test_Metadata():

    # Metadata class instances should:
    # - TODO

    metadata = Metadata()
    assert(isinstance(metadata,Metadata))







def test_PointList():

    # PointList class instances should:
    # - TODO

    dtype = [
        ('x',int),
        ('y',float)
    ]
    data = np.zeros(10,dtype=dtype)
    pointlist = PointList(
        data=data
    )
    assert(isinstance(pointlist,PointList))

def test_PointListArray():

    # PointListArray class instance should:
    # - TODO

    dtype = [
        ('x',int),
        ('y',float)
    ]
    shape = (5,5)
    pointlistarray = PointListArray(
        dtype = dtype,
        shape = shape
    )
    assert(isinstance(pointlistarray,PointListArray))








