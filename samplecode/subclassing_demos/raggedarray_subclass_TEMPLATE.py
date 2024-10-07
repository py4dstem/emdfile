from emdfile import PointListArray, Metadata, _read_metadata
import numpy as np
from os.path import basename

class PointListArraySubclass_TEMPLATE(PointListArray):
    """
    An emdfile pointlistarray subclass template.

    There are two required methods:
        __init__
        _get_constructor_args

    And two optional methods:
        _populate_instance
        to_h5

    The __init__ method should accept the `name` argument and pass its value
    to Array.__init__, which should be called.

    _get_constructor_args should return a dictionary of keyword:value
    arguments that will be passed to the __init__ method when class
    instances are created while reading from disk.

    If _populate_instance is defined then it's run when reading this object from
    an H5 file after instantiation, enabling additional setup or configuration.

    .to_h5 is already defined, and handles storing data and metadata. If
    additional customization is desired, .to_h5 can be overwritten, however
    in this case the parent class' .to_h5 method should be run to create the
    HDF5 group and to save the normal data and metadata. It accepts the
    h5py.Group of the parent node.
    """
    def __init__(
        self,
        name = 'my_pointlistarray_subclass'
        *args,
        **kwargs
        ):
        """
        Required. Should call PointListArray.__init__.
        """
        # code..
        # Initialize as the parent class
        PointListArray.__init__(
            self,
            name = name,
            dtype = dtype,
            shape = shape
        )
        # code..
        pass

    # Read methods
    # This method is required.
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Required. Must return a dictionary representing arguments which will
        be passed to __init__ at read time.
        """
        # Retrieve PointListArray constructor args
        pointlistarray_constr_args = PointListArray._get_constructor_args(group)
        # Retrieve Metadata dictionaries
        some_metadata = _read_metadata(group,'name')
        # code..
        # make the dictionary of constructor arguments
        constructor_args = {
            'name' : basename(group.name),
            'data' : pointlistarray_constr_args['data'],
            'thing' : some_metadata['thing']
            # etc.
        }
        # return
        return constructor_args

    # This method is optional
    def _populate_instance(self,group):
        """
        Optional.  During read, this method is run after object instantiation.

        Note that PointListArray already has a _populate instance method which
        will add the ragged data array after instantiation if a new
        _populate_instance is not defined. It does so by *concatenating* the
        data array from the H5 to the new instance, so if any data is added
        earlier, e.g. in __init__, this could lead to unexpected behavior.

        In the example below we assume that the __init__ method added some
        data to the class that we want to overwrite; we do so by first
        removing any data currently stored, and then running
        PointListArray._populated instance.
        """
        # remove any existing data
        for (x,y) in np.ndindex(self.shape):
            self[x,y] = np.zeros(0,dtype=self.dtype)
        # add data from the h5 file
        PointListArray._populate_instance(self,group)
        pass

    # Write methods
    # This method is optional
    def to_h5(self,group):
        """
        Optional. If defined, should call PointListArray.to_h5(self,group) to handle
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
        PointListArray.to_h5(self,group)

