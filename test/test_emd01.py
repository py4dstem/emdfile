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
        def temp_file(self):
            tt = tempfile.NamedTemporaryFile(mode='wb')
            tt.close()  # need to close the file to use it later
            return Path(tt.name)
        
        @pytest.fixture
        def _make_data(self, temp_file):
            # Create a 0.1 (or 0.2?) version EMD

            data = np.random.rand(100,100)

            with h5py.File(temp_file, 'w') as f0:
                f0.attrs['version_major'] = 0
                f0.attrs['version_minor'] = 1
                f0.create_group('/data')
                f0.create_group('/microscope')
                f0.create_group('/user')
                f0.create_group('/sample')

                group_top = f0.create_group('/data/test_data')
                group_top.attrs['emd_group_type'] = int(1)
                group_top.create_dataset('data', data=data)
                dim1 = group_top.create_dataset('dim1', data=range(100))
                dim1.attrs['name'] = 'Y'
                dim1.attrs['units'] = 'pixels'
                dim2 = group_top.create_dataset('dim2', data=range(100))
                dim2.attrs['name'] = 'X'
                dim2.attrs['units'] = 'pixels'
            return temp_file
        
        def test_make_data(self, _make_data):
            assert _make_data.exists()
            
            with h5py.File(_make_data,'r') as f0:
                assert isinstance(f0['/data/test_data'], h5py.Group)