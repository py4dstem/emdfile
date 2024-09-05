from emdfile import Metadata
#from os.path import join,exists
#from emdfile import _TESTPATH
#from emdfile import save, read
#import numpy as np

# Set paths
#dirpath = _TESTPATH
#testpath = join(dirpath,"test_base_classes.h5")

class TestMetadata:

    def setup_method(self):
        self.x = Metadata()

    def test_instantiation(self):
        assert(isinstance(self.x,Metadata))
        pass

