from emdfile import Array, Metadata, _read_metadata
import numpy as np
from os.path import basename

class ArraySubclass_TEMPLATE(Array):
    """
    An emdfile array subclass template.

    There are two required methods: __init__, and _get_constructor_args.

    The __init__ method should call Array.__init__.

    _get_constructor_args is required for reading the class.  When the
    emdfile read() function finds an H5 group representing this class,
    this method is called.  It should collect and return a dictionary
    representing arguments that will be passed to the __init__ method.

    There are two optional methods: _populate_instance and to_h5.

    If _populate method is defined then run when reading this object from
    an H5 file, this method is run after instantiation, enabling additional
    setup or configuration.

    emdfile classes already have a .to_h5 method defined, which will handle
    storing the data, the emdfile class' native metadata (e.g its name, dim
    vectors, fields, shapes), and metadata stored in the .metadata property. If
    additional customization is desired, the .to_h5 method can be overwritten.
    In this case, the parent class' .to_h5 method should be run to save the
    normal data and metadata.
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

        # code
        # ...
        # ...

        # Initialize as the parent class
        Array.__init__(
            self,
            name = name,
            data = data
        )

        # code
        # ...
        # ...

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

        # code
        # ...
        # ...

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



