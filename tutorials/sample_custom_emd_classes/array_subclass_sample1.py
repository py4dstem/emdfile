# This file defines a minimal subclass of Array


from emdfile import Array
import numpy as np
from os.path import basename

class SimpleArraySubclass(Array):
    """
    """

    def __init__(
        self,
        data,
        name = 'a_simple_array',
        **kwargs
        ):
        """
        """
        # Initialize as the parent class
        Array.__init__(
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
        array_constr_args = Array._get_constructor_args(group)

        # return them
        return array_constr_args



