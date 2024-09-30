from emdfile import save,read,set_author,set_program
import numpy as np
import pytest
import tempfile
from pathlib import Path

import h5py
from emdfile.utils import _is_EMD_file,_get_EMD_rootgroups
from emdfile.classes import (
    Node,
    Root,
    Metadata,
    Array,
    PointList,
    PointListArray
)


class TestHeader:

    @pytest.fixture
    def array(self):
        """Make an array"""
        return Array(
            data = np.arange(np.prod((2,3))).reshape((2,3)))

    @pytest.fixture
    def testpath(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    def test_header(self,array,testpath):
        """Save a file and check its header tags"""
        # save
        save(testpath,array)
        # check tags
        with h5py.File(testpath,'r') as f:
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

    def test_header2(self,array,testpath):
        """ Save a file after modifying the authoring user, then
        check its header tags
        """
        set_author('emdfile_test_suite')
        set_program('emdfile_test_suite')
        # save
        save(testpath,array)
        # check tags
        with h5py.File(testpath,'r') as f:
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
            assert( f.attrs['authoring_program'] == 'emdfile_test_suite' )
            assert( f.attrs['authoring_user'] == 'emdfile_test_suite' )
            uuid = f.attrs['UUID']
            assert(isinstance(uuid,str))



