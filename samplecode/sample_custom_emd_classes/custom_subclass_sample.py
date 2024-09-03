from emdfile import Custom, Metadata, _read_metadata
import numpy as np
from os.path import basename

class CustomSubclass(Custom):
    """
    """

    def __init__(
        self,
        x,
        y,
        name = 'custom_subclass',
        ):
        """
        x,y are ints
        """
        Custom.__init__(
            self,
            name = name,
        )

        # attributes which are emdfile classes get saved
        self.x = Array(
            name = 'x',
            data = np.full((2,2),x)
        )
        self.y = PointList(
            name = 'y',
            data = np.full(5,y,dtype=[('a',int),('b',float)])
        )

        pass



    # Read methods

    @classmethod
    def _get_constructor_args(cls,group):
        """
        """
        # get data
        emd_data = cls._get_emd_attr_data(cls,group)

        # get arguments
        constructor_args = {
            'name' : basename(group.name),
            'x' : emd_data['x'],
            'y' : some_metadata['thing']
            # etc.
        }

        # return
        return constructor_args



    # This method is optional

    def _populate_instance(self,group):
        """
        Optional.  During read, this method is run after object instantiation.
        """
        pass




    # Write methods

    # This method is optional

    def to_h5(self,group):
        """
        Optional. If defined, should call Custom.to_h5(self,group) to handle
        saving the parent class' data/metadata.
        """
        # Here some class attributes are stored in a Metadata dict which is
        # placed in the .metadata propetry, such that it's saved in the 
        # subsequent `to_h5` call
        self.metadata = Metadata(
            name = '_attr_metadata',
            data = {
                'x' : self.x,
                'y' : self.y
            }
        )
        Custom.to_h5(self,group)





