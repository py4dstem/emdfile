from emdfile import Custom
#from os.path import join,exists
#from emdfile import _TESTPATH
#from emdfile import save, read
#import numpy as np

# Set paths
#dirpath = _TESTPATH
#testpath = join(dirpath,"test_base_classes.h5")


class test_Custom:

    def setup_method(self):
        """ Instantiate a custom object
        """
        self.x = Custom()

    def test_instantiation(self):
        assert(isinstance(self.x,Custom))
        pass


