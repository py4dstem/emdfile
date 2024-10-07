from emdfile import Array, Metadata, _read_metadata
from os.path import basename

class ArraySubclass_TEMPLATE(Array):
    """
    An emdfile array subclass template.

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
        name = 'my_array_subclass'
        *args,
        **kwargs
        ):
        """
        Required. Should call Array.__init__.
        """
        # code...

        # Initialize as the parent class
        Array.__init__(
            self,
            name = name,
            data = data
        )

        # code...
        pass

    # Read methods
    # This method is required.
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Required. Must return a dictionary representing arguments which will
        be passed to __init__ at read time.
        """
        # Retrieve Array constructor args
        array_constr_args = Array._get_constructor_args(group)
        # Retrieve Metadata dictionaries
        some_metadata = _read_metadata(group,'name')
        # code...
        # make the dictionary of constructor arguments
        constructor_args = {
            'name' : basename(group.name),
            'data' : array_constr_args['data'],
            'thing' : some_metadata['thing']
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
        Optional. If defined, should call Array.to_h5(self,group) to handle
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
        Array.to_h5(self,group)

