"""
Tests for the emd version 0.1 reader.

For pytest
"""

import pytest

from pathlib import Path
import tempfile
#from os.path import join,exists
#from os import remove

import numpy as np
from numpy import array_equal
import h5py

from emdfile.read_EMD_v0p1 import read_EMD_v0p1, emd_v0p1


from emdfile import _TESTPATH
from emdfile import save,read
from emdfile.read import _is_EMD_file,_get_EMD_rootgroups
from emdfile.classes import (
    Node,
    Root,
    Metadata,
    Array,
    PointList,
    PointListArray
)

class TestEMD01:
    
        @pytest.fixture
        def _temp_file(self):
            """Create an empty temporary file and return as a Path."""
            tt = tempfile.NamedTemporaryFile(mode='wb')
            tt.close()  # need to close the file to use it later
            return Path(tt.name)
        
        @pytest.fixture
        def _make_data(self):
            """Create a v0.1 (or 0.2?) version EMD using a temporary file. Returns a Path
            to the file.
            """
            """Create an empty temporary file and return as a Path."""
            tt = tempfile.NamedTemporaryFile(mode='wb')
            tt.close()  # need to close the file to use it later
            _temp_file = Path(tt.name)
            
            data = np.random.rand(100, 100)

            with h5py.File(_temp_file, 'w') as f0:
                f0.attrs['version_major'] = 0
                f0.attrs['version_minor'] = 1
                data_top = f0.create_group('/data')
                f0.create_group('/microscope')
                f0.create_group('/user')
                f0.create_group('/sample')

                group_top = data_top.create_group('test_data')
                group_top.attrs['emd_group_type'] = int(1)
                group_top.create_dataset('data', data=data)
                dim1 = group_top.create_dataset('dim1', data=range(100))
                dim1.attrs['name'] = 'Y'
                dim1.attrs['units'] = 'pixels'
                dim2 = group_top.create_dataset('dim2', data=range(100))
                dim2.attrs['name'] = 'X'
                dim2.attrs['units'] = 'pixels'
            return _temp_file
        
        @pytest.fixture
        def _make_data_2(self):
            """Create a v0.1 (or 0.2?) version EMD using a temporary file. Returns a Path
            to the file.
            """
            tt = tempfile.NamedTemporaryFile(mode='wb')
            tt.close()  # need to close the file to use it later
            _temp_file = Path(tt.name)
            
            with h5py.File(_temp_file, 'w') as f0:
                f0.attrs['version_major'] = 0
                f0.attrs['version_minor'] = 2
                data_top = f0.create_group('/data')
                f0.create_group('/microscope')
                f0.create_group('/user')
                f0.create_group('/sample')
                for ii in range(2):
                    data = np.random.rand(100, 100)
                    group_name = f'test_data{ii}'
                    group_top = data_top.create_group(group_name)
                    group_top.attrs['emd_group_type'] = int(1)
                    group_top.create_dataset('data', data=data)
                    dim1 = group_top.create_dataset('dim1', data=range(100))
                    dim1.attrs['name'] = 'Y'
                    dim1.attrs['units'] = 'pixels'
                    dim2 = group_top.create_dataset('dim2', data=range(100))
                    dim2.attrs['name'] = 'X'
                    dim2.attrs['units'] = 'pixels'
            return _temp_file
        
        def test_make_data(self, _make_data):
            """Test that the temporary data is created with the emd v0.1 format."""
            assert _make_data.exists()
            
            with h5py.File(_make_data,'r') as f0:
                assert isinstance(f0['/data/test_data'], h5py.Group)
        
        def test_not_emd1(self, _make_data):
            """Ensure it is not seen as a emd v1.0"""
            assert not _is_EMD_file(_make_data)
            
        def test_read(self, _make_data):
            new_emd = read_EMD_v0p1(_make_data)

        def test_read2(self, _make_data_2):
            new_emd = read_EMD_v0p1(_make_data_2)

