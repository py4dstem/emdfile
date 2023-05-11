from emdfile import PointListArray, Metadata, _read_metadata
import numpy as np

class PointListArraySubclass(PointListArray):
    """
    """

    def __init__(
        self,
        shape,
        name = 'my_pointlistarray_subclass',
        ):
        """
        A 2D ragged array of float32's. Shape must be a 2-tuple.
        Initializes empty.
        """

        # initialize
        PointListArray.__init__(
            self,
            name = name,
            dtype = np.float32,
            shape = shape
        )

        pass



    # Read methods
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Returns a dictionary of arguments to pass to __init__
        """
        # get array constructor args
        kwargs = PointListArray._get_constructor_args(group)

        # make the dictionary of constructor arguments and return
        constructor_args = {
            'shape' : kwargs['shape'],
            'name' : kwargs['name']
        }
        return constructor_args


    # PointListArray already has a _populate instance method which
    # will add the ragged data array.




