from emdfile import Custom, Metadata, _read_metadata
from os.path import basename

class CustomSubclass_TEMPLATE(Custom):
    """
    An emdfile custom subclass template.

    In a Custom subclass, any class attributes with values equal to another
    emdfile class will be saved with the class instance.

    There are two required methods:
        __init__
        _get_constructor_args

    There are two optional methods:
        to_h5
        _populate_instance

    The __init__ method should call Custom.__init__ and pass a name through.

    _get_constructor_args should return a dictionary of keyword:value
    arguments that will be passed to the __init__ method when class
    instances are created while reading from disk.

    .to_h5 is already defined, and handles storing data and metadata. If
    additional customization is desired, .to_h5 can be overwritten, however
    in this case the parent class' .to_h5 method should be run to create the
    HDF5 group, save all node-like attributes, and save metadata. It accepts the
    h5py.Group of the parent node.

    The _populate instance method is required for Custom subclasses. This is
    because the Custom class I/O is, in some sense, half complete: the special
    thing Custom nodes do, i.e. store node-like data as attributes, is handled
    correctly and automoatically when writing to files by the .to_h5 method,
    however, is not yet handled when reading from files. To this end, the
    _populate_instance method should be defined, it should read data-node like
    subgroups into Python using _get_emd_attr_data, and it should assing that
    data to attributes as appropriate.
    """
    def __init__(
        self,
        name = 'my_custom_subclass'
        *args,
        **kwargs
        ):
        """
        Required. Should call Custom.__init__.
        """
        # code...
        # Initialize as the parent class
        Custom.__init__(
            self,
            name = name,
        )
        # Any class attribute with a value equal to
        # an emdfile class will be saved
        self.some_data = Array(
            name = 'some_data_array',
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
        # Retrieve emdfile class instances assigned to attributes
        emd_data = cls._get_emd_attr_data(cls,group)
        # Retrieve Metadata dictionaries
        some_metadata = _read_metadata(group,'name')
        # code...
        # make the dictionary of constructor arguments
        constructor_args = {
            'name' : basename(group.name),
            'data' : emd_data['data'],
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

