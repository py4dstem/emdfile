from emdfile import PointList, Metadata, _read_metadata
import numpy as np

class PointListSubclass(PointList):
    """
    """

    def __init__(
        self,
        fields,
        length,
        name = 'my_points_subclass',
        ):
        """
        fields is a list of strings and length is an int.
        """

        # make the data
        data = np.zeros(
            length,
            dtype = [(x,np.float32) for x in fields]
        )

        # initialize
        PointList.__init__(
            self,
            name = name,
            data = data
        )

        pass



    # Read methods
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Returns a dictionary of arguments to pass to __init__
        """
        # get array constructor args
        kwargs = PointList._get_constructor_args(group)
        name = kwargs['name']
        data = kwargs['data']

        # make the dictionary of constructor arguments and return
        constructor_args = {
            'fields' : data.dtype.names,
            'length' : len(data),
            'name' : name
        }
        return constructor_args


    def _populate_instance(self,group):
        """
        If we don't define this method, the class will write and read successfully -
        however, because the class __init__ method creates a new data array populated
        by zeros, a class instance loaded from an H5 *won't* point to the data array
        from H5.  (If this was all this class did, we probably wouldn't want the
        constructor to look like this for this reason - let's assume there's some
        reason it needs to be this way!). Adding this method re-assigns the data
        array to the data stored in the H5.
        """
        # get the data
        kwargs = PointList._get_constructor_args(group)
        data = kwargs['data']

        # re-assign .data
        self.data = data

        pass




