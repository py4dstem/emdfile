from emdfile import PointListArray
import numpy as np
import pytest

class TestPointListArray():

    @pytest.fixture
    def pla(self):
        """Make a PointListArray"""
        dtype = [('x',np.int32),('y',np.float32)]
        pla = PointListArray(
            dtype = dtype,
            shape = (5,5),
        )
        return pla

    def test_pointlistarray(self,pla):
        assert(isinstance(pla,PointListArray))
        pass

