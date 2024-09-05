from emdfile import PointListArray
#from os.path import join,exists
#from emdfile import _TESTPATH
#from emdfile import save, read
import numpy as np

# Set paths
#dirpath = _TESTPATH
#testpath = join(dirpath,"test_base_classes.h5")

class TestPointListArray():

    def setup_method(self):
        """ instantiate a PointList
        """
        dtype = [('x',np.int32),('y',np.float32)]

        pla = PointListArray(
            dtype = dtype),
            shape = (5,5)
        )
        self.x = pla
        pass

    def test_instantiation(self):
        assert(isinstance(self.x,PointListArray))
        pass

