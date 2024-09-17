from emdfile import Array,save,read
import numpy as np
from os.path import join,exists
from pathlib import Path
import tempfile
import pytest

# Set paths

class TestArray():

    @pytest.fixture
    def _tempfile(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    @pytest.fixture
    def array(self):
        """Create an Array instance"""
        s = (3,4,5,6,7)
        d = np.arange(np.prod(s)).reshape(s)
        ar = Array(
            data = d,
            name = 'test_array',
            dims = [
                [0,1],
                [0,5,6,10],
                [2,3],
                5,
                # final dimension test autopopulate
            ],
            dim_units = [
                'nm',
                'um',
                'mm',
                # 4th+5th dim units test autopopulate
            ],
            dim_names = [
                'a',
                'b',
                'c',
                # 4th+5th dim names test autopopulate
            ],
        )
        return ar

    @pytest.fixture
    def arraystack(self):
        """Create a stack=True Array instance"""
        s = (3,50,60)
        d = np.arange(np.prod(s)).reshape(s)
        ar = Array(
            data = d,
            name = 'test_stackarray',
            dims = [
                [0,2],
                [0,2],
            ],
            dim_units = [
                'nm',
                'nm',
            ],
            dim_names = [
                'x',
                'y',
                # 4th+5th dim names test autopopulate
            ],
            slicelabels = [
                'A',
                'B',
                'C'
            ]
        )
        return ar

    def test_instantiation(self):
        """instantiate an Array"""
        s = (3,4,5)
        d = np.arange(np.prod(s)).reshape(s)
        ar = Array(
            data = d
        )
        assert(isinstance(ar, Array))

    def test_array(self,array,_tempfile):
        """test different dims, dim_units, dim_names instantiation options"""
        ar = array
        # dims
        assert(np.array_equal( ar.dim(0), np.arange(3)))
        assert(np.array_equal( ar.dim(1), np.array([0,5,6,10])))
        assert(np.array_equal( ar.dim(2), np.arange(2,7)))
        assert(np.array_equal( ar.dim(3), np.arange(0,30,5)))
        assert(np.array_equal( ar.dim(4), np.arange(7)))
        # dim units
        assert(ar.dim_units[0] == 'nm')
        assert(ar.dim_units[1] == 'um')
        assert(ar.dim_units[2] == 'mm')
        assert(ar.dim_units[3] == 'unknown')
        assert(ar.dim_units[4] == 'pixels')
        # dim names
        assert(ar.dim_names[0] == 'a')
        assert(ar.dim_names[1] == 'b')
        assert(ar.dim_names[2] == 'c')
        assert(ar.dim_names[3] == 'dim3')
        assert(ar.dim_names[4] == 'dim4')
        # save / read
        save(_tempfile,ar)
        ar2 = read(_tempfile)
        # confirm successful read
        assert(np.array_equal(ar.data, ar2.data))
        # dims
        assert(np.array_equal( ar2.dim(0), np.arange(3)))
        assert(np.array_equal( ar2.dim(1), np.array([0,5,6,10])))
        assert(np.array_equal( ar2.dim(2), np.arange(2,7)))
        assert(np.array_equal( ar2.dim(3), np.arange(0,30,5)))
        assert(np.array_equal( ar2.dim(4), np.arange(7)))
        # dim units
        assert(ar2.dim_units[0] == 'nm')
        assert(ar2.dim_units[1] == 'um')
        assert(ar2.dim_units[2] == 'mm')
        assert(ar2.dim_units[3] == 'unknown')
        assert(ar2.dim_units[4] == 'pixels')
        # dim names
        assert(ar2.dim_names[0] == 'a')
        assert(ar2.dim_names[1] == 'b')
        assert(ar2.dim_names[2] == 'c')
        assert(ar2.dim_names[3] == 'dim3')
        assert(ar2.dim_names[4] == 'dim4')
        pass


    def test_stack(self,arraystack,_tempfile):
        """test instantiating a stack Array"""
        ar = arraystack
        # dims
        assert(np.array_equal( ar.dim(0), np.arange(0,100,2)))
        assert(np.array_equal( ar.dim(1), np.arange(0,120,2)))
        # dim units
        assert(ar.dim_units[0] == 'nm')
        assert(ar.dim_units[1] == 'nm')
        # dim names
        assert(ar.dim_names[0] == 'x')
        assert(ar.dim_names[1] == 'y')
        # slices
        assert(np.array_equal(ar['A'].data,ar[0]))
        assert(np.array_equal(ar['B'].data,ar[1]))
        assert(np.array_equal(ar['C'].data,ar[2]))
        # save / read
        save(_tempfile,ar)
        ar2 = read(_tempfile)
        # confirm successful read
        assert(np.array_equal(ar.data, ar2.data))
        # dims
        assert(np.array_equal( ar2.dim(0), np.arange(0,100,2)))
        assert(np.array_equal( ar2.dim(1), np.arange(0,120,2)))
        # dim units
        assert(ar2.dim_units[0] == 'nm')
        assert(ar2.dim_units[1] == 'nm')
        # dim names
        assert(ar2.dim_names[0] == 'x')
        assert(ar2.dim_names[1] == 'y')
        # slices
        assert(np.array_equal(ar2['A'].data,ar2[0]))
        assert(np.array_equal(ar2['B'].data,ar2[1]))
        assert(np.array_equal(ar2['C'].data,ar2[2]))
        pass


    def test_Array_complex_readwrite(self,_tempfile):
        # make array
        d = np.exp(1j*np.linspace(0,2*np.pi)).astype(np.complex64)
        ar = Array(
            data = d
        )
        # save, read, check
        save(_tempfile,ar,mode='o')
        ar2 = read(_tempfile)
        assert(np.array_equal(ar.data,ar2.data))

    def test_Array_stackarray(self,_tempfile):
        # make array
        x = Array(np.zeros((3,5,6)),slicelabels=['a','b','c'])
        # save
        save(_tempfile,x,mode='o')
        # read
        y = read(_tempfile)
        # compare
        assert(x.depth == y.depth)
        assert(x.rank == y.rank)
        assert(x.shape == y.shape)
        assert(x.slicelabels == y.slicelabels)

    def test_Array_dimvects(self,_tempfile):
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
        save(_tempfile,ar,mode='o')
        ar2 = read(_tempfile)

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

