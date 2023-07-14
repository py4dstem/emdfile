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


    def test_Array_stackarray(self):

        # make array
        x = Array(np.zeros((3,5,6)),slicelabels=['a','b','c'])

        # save
        save(testpath,x,mode='o')

        # read
        y = read(testpath)

        # compare
        assert(x.depth == y.depth)
        assert(x.rank == y.rank)
        assert(x.shape == y.shape)
        assert(x.slicelabels == y.slicelabels)




    def test_Array_dimvects(self):

        dims = (
            [0,0.5],
            None,
            [0,3,4,5,9,100]
        )

        # make array
        shape = (4,5,6,8)
        data_shape = tuple([3]+list(shape))
        d = np.arange(np.prod(data_shape)).reshape(data_shape)
        ar = Array(
            data = d,
            dims = dims,
            slicelabels = ['a','b','c']
        )


        # check that...

        # ...the last (3'rd) dim instantiated in integer pixels
        assert(np.array_equal(
            ar.dim(3),
            np.arange(shape[3])
        ))
        # ...the 2nd dim instantiated as written
        assert(np.array_equal(
            ar.dim(2),
            np.array(dims[2])
        ))
        # ...the 1st dim expanded correctly to pixels
        assert(np.array_equal(
            ar.dim(1),
            np.arange(shape[1])
        ))
        # ...the 0th dim expanded correctly
        assert(np.array_equal(
            ar.dim(0),
            np.arange(shape[0])*0.5
        ))

        # ...dim names are correct
        assert(ar.dim_names[0] == 'dim0')
        assert(ar.dim_names[1] == 'dim1')
        assert(ar.dim_names[2] == 'dim2')
        assert(ar.dim_names[3] == 'dim3')

        # ... the dim units are correct
        assert(ar.dim_units[0] == 'unknown')
        assert(ar.dim_units[1] == 'pixels')
        assert(ar.dim_units[2] == 'unknown')
        assert(ar.dim_units[3] == 'pixels')

        # modify a dim and then check it
        new_dim = np.array([-3,-1.1,0.8,1.12,2.5])
        ar.set_dim(
            1,
            new_dim,
            units = 'cows',
            name = 'fields'
        )
        assert(np.array_equal(
            ar.dim(1),
            new_dim
        ))
        assert(ar.dim_units[1] == 'cows')
        assert(ar.dim_names[1] == 'fields')



        # save, read
        save(testpath,ar,mode='o')
        ar2 = read(testpath)

        # check...

        # data
        assert(array_equal(ar.data,ar2.data))

        # dims
        assert(array_equal(ar.dim(0), ar2.dim(0)))
        assert(array_equal(ar.dim(1), ar2.dim(1)))
        assert(array_equal(ar.dim(2), ar2.dim(2)))
        assert(array_equal(ar.dim(3), ar2.dim(3)))

        # dim names
        assert(ar.dim_names[0] == ar2.dim_names[0])
        assert(ar.dim_names[1] == ar2.dim_names[1])
        assert(ar.dim_names[2] == ar2.dim_names[2])
        assert(ar.dim_names[3] == ar2.dim_names[3])

        # dim units
        assert(ar.dim_units[0] == ar2.dim_units[0])
        assert(ar.dim_units[1] == ar2.dim_units[1])
        assert(ar.dim_units[2] == ar2.dim_units[2])
        assert(ar.dim_units[3] == ar2.dim_units[3])

        # slices
        assert(array_equal( ar['a'].data, ar2['a'].data ))
        assert(array_equal( ar['b'].data, ar2['b'].data ))
        assert(array_equal( ar['c'].data, ar2['c'].data ))






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








