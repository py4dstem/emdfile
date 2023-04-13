import numpy as np
from os.path import join,exists
from os import remove
from numpy import array_equal
import h5py

from emdfile import _TESTPATH
from emdfile import save,read,set_author
from emdfile.read import _is_EMD_file,_get_EMD_rootgroups
from emdfile.classes import (
    Node,
    Root,
    Metadata,
    Array,
    PointList,
    PointListArray
)

# Set paths
dirpath = _TESTPATH
path_h5 = join(dirpath,"test.h5")





class TestHeader:

    ## Setup and teardown

    @classmethod
    def setup_class(cls):
        cls._clear_files(cls)
        cls._make_data(cls)

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        self._clear_files()

    def _make_data(self):
        """ Make
            - an array
            - an array with some 'slicelabels'
            #- a pointlist
            #- a pointlistarray
        """
        # arrays
        self.array = Array(
            data = np.arange(np.prod((2,3))).reshape((2,3))
        )



    def _clear_files(self):
        """
        Delete h5 files which this test suite wrote
        """
        paths = [
            path_h5
        ]
        for p in paths:
            if exists(p):
                remove(p)





    ## Tests

    def test_header(self):
        """ Save a file, and check its header tags
        """
        # save
        save(path_h5,self.array)

        # check tags
        with h5py.File(path_h5,'r') as f:
            for key in (
                'emd_group_type',
                'version_major',
                'version_minor',
                'authoring_program',
                'authoring_user',
                'UUID'
            ):
                assert( key in f.attrs )

            assert( f.attrs['emd_group_type'] == 'file' )
            assert( f.attrs['version_major'] == 1 )
            assert( f.attrs['version_minor'] == 0 )
            assert( f.attrs['authoring_program'] == 'emdfile' )
            assert( f.attrs['authoring_user'] == '' )
            uuid = f.attrs['UUID']
            assert(isinstance(uuid,str))



    def test_header2(self):
        """ Save a file after modifying the authoring user, then
        check its header tags
        """
        set_author('emdfile_test_suite')


        # save
        save(path_h5,self.array)

        # check tags
        with h5py.File(path_h5,'r') as f:
            for key in (
                'emd_group_type',
                'version_major',
                'version_minor',
                'authoring_program',
                'authoring_user',
                'UUID'
            ):
                assert( key in f.attrs )

            assert( f.attrs['emd_group_type'] == 'file' )
            assert( f.attrs['version_major'] == 1 )
            assert( f.attrs['version_minor'] == 0 )
            assert( f.attrs['authoring_program'] == 'emdfile' )
            assert( f.attrs['authoring_user'] == 'emdfile_test_suite' )
            uuid = f.attrs['UUID']
            assert(isinstance(uuid,str))



