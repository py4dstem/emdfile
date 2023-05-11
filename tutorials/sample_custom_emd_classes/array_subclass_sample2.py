# This file defines a subclass of Array
# which contains a data array and a few attributes


from emdfile import Array, Metadata, _read_metadata
import numpy as np
from os.path import basename

class ArraySubclass(Array):
    """
    """

    def __init__(
        self,
        data,
        name = 'my_array_subclass',
        color = 'blue',
        number = 7,
        elephants = True
        ):
        """
        For some tuple `shape`, makes a data array of this
        shape and wraps it as an Array instance.
        """
        # Initialize as the parent class
        Array.__init__(
            self,
            name = name,
            data = data
        )

        # Assign attributes
        self.color = color
        self.number = number
        self.elephants = elephants

        pass



    # Read methods
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Returns a dictionary of arguments to pass to __init__
        """
        # get array constructor args
        array_constr_args = Array._get_constructor_args(group)

        # get metadata
        md = _read_metadata(group,'_attr_metadata')

        # make the dictionary of constructor arguments and return
        constructor_args = {
            'name' : basename(group.name),
            'data' : array_constr_args['data'],
            'color' : md['color'],
            'number' : md['number'],
            'elephants' : md['elephants']
        }
        return constructor_args


    # Write methods
    def to_h5(self,group):
        """
        Store the extra class attributes as metadata before saving
        """
        self.metadata = Metadata(
            name = '_attr_metadata',
            data = {
                'color' : self.color,
                'number' : self.number,
                'elephants' : self.elephants,
            }
        )
        Array.to_h5(self,group)


