# Demos use of the emd.Custom class


from typing import Optional,Union
import numpy as np
from os.path import basename

from emdfile import (
    Custom,
    Array,
    PointList,
    Metadata
)



class MyArrayClass(Array):
    """ A very simple Array subclass
    """

    def __init__(
        self,
        data,
        name = 'my_array_class'
        ):
        """ `data` is a numpy array
        """
        Array.__init__(self,name=name,data=data)

    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Returns a dictionary of args/values to pass to the class constructor
        """
        ar_constr_args = Array._get_constructor_args(group)
        args = {
            'data' : ar_constr_args['data'],
            'name' : ar_constr_args['name'],
        }
        return args


class MyPointsClass(PointList):
    """ A PointList subclass with specified dimension fields and metadata
    """

    def __init__(
        self,
        x,
        y,
        name = 'my_points_class'
        ):
        """ `x` and `y` are 1D arrays of the same length
        """
        data = np.empty(
            len(x),
            dtype = [
                ('x','>f8'),
                ('y','>f8'),
            ]
        )
        data['x'],data['y'] = x,y

        PointList.__init__(self,name=name,data=data)

        self.metadata = Metadata(
            name = 'metadata',
            data = {
                'length' : len(data)
            }
        )

    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Returns a dictionary of args/values to pass to the class constructor
        """
        pl_constr_args = PointList._get_constructor_args(group)
        args = {
            'x' : pl_constr_args['data']['x'],
            'y' : pl_constr_args['data']['y'],
            'name' : pl_constr_args['name'],
        }
        return args



class MyCustomClass(Custom):
    """ A class holding two Arrays and some metadata
    """

    def __init__(
        self,
        data,
        name = 'my_custom_class'
        ):
        """ `data` is a numpy array
        """
        Custom.__init__(self,name=name)


        # define some data arrays
        self.data = Array(
            data = data,
            name = 'data'
        )
        self.moredata = Array(
            data = np.tile(data,(2,2)),
            name = 'moredata'
        )


        # add some metadata
        self.metadata = Metadata(
            name = 'my_metadata',
            data = {
                'cats' : 'aregreat'
            }
        )



    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        """
        # get EMD group data
        emd_data = cls._get_emd_attr_data(cls,group)

        kwargs = {
            'name' : basename(group.name),
            'data' : emd_data['data'].data
        }

        return kwargs


