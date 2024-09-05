from emdfile import Array
from os.path import join,exists
from emdfile import _TESTPATH
from emdfile import save, read
import numpy as np

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
        assert(np.array_equal(ar.data,ar2.data))

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
        # ...data
        assert(np.array_equal(ar.data,ar2.data))
        # ...dims
        assert(np.array_equal(ar.dim(0), ar2.dim(0)))
        assert(np.array_equal(ar.dim(1), ar2.dim(1)))
        assert(np.array_equal(ar.dim(2), ar2.dim(2)))
        assert(np.array_equal(ar.dim(3), ar2.dim(3)))
        # ...dim names
        assert(ar.dim_names[0] == ar2.dim_names[0])
        assert(ar.dim_names[1] == ar2.dim_names[1])
        assert(ar.dim_names[2] == ar2.dim_names[2])
        assert(ar.dim_names[3] == ar2.dim_names[3])
        # ...dim units
        assert(ar.dim_units[0] == ar2.dim_units[0])
        assert(ar.dim_units[1] == ar2.dim_units[1])
        assert(ar.dim_units[2] == ar2.dim_units[2])
        assert(ar.dim_units[3] == ar2.dim_units[3])
        # ...slices
        assert(np.array_equal( ar['a'].data, ar2['a'].data ))
        assert(np.array_equal( ar['b'].data, ar2['b'].data ))
        assert(np.array_equal( ar['c'].data, ar2['c'].data ))

