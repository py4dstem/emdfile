import emdfile import Custom, Array, Metadata, _read_metadata
import numpy as np

class TEMPLATE_CustomClass(Custom):
     """
     An emdfile Custom class template.

     Any class attributes which are themselves emdfile nodes (i.e. Array,
     PointList,PointListArray instances) will be saved with this object.

     To read correctly, the ._get_constructor_args() method needs to be
     defined.  This method is run when reading this object from an H5 file
     is attempted. It must return a dictionary, which will be passed
     directly to the class __init__ method, and therefore must contain
     keys corresponding to the __init__ method's arguments.

     Optionally, the ._populate_instance() method may be defined. This
     method is run when reading this object from an H5 file, but after
     the object has been instantiated using .get_contructor_args + __init__.
     Any post-instantiation configuration can be performed using this method.

     Custom objects already have a .to_h5 method defined, which will handle
     storing emdfile class-like attributes and metadata, as noted above.
     If additional customization is required, the .to_h5 method can be
     overwritten.  In this case, Custom.to_h5() should be run at some
     point inside the new .to_h5 method, to ensure that those attributes
     and metadata are still saved.

     Examples below.
     """

    def __init__(
        self,
        name = 'my_custom_class'
        *args,
        **kwargs
        ):
        """
        The only required argument is 'name'.

        This method should call Custom.__init__(self,name=name).
        """

        # Initialize as an emdfile Custom object
        Custom.__init__(self,name=name)


        # code
        # ...
        # ...

        # storing an emdfile class instance as an attribute will cause
        # it to be saved and read again by the class read/write methods
        self._some_data = Array(
            name='some_data',
            data=np.zeros((2,2))
        )

        # any number of metadata dictionaries can be stored in the
        # .metadata property, and will be saved/read automatically with
        # the normal read/write methods. Assignment to the .metadata
        # property adds the new Metadata instance to a running dictionary
        self.metadata = Metadata(
            name = 'i_never_metadata_i_didnt_like',
            data = {
                'x' : 1,
                'y' : (2,3,4),
                'z' : np.ones((3,3))
            }
        )
        self.metadata = Metadata(
            name = 'metadata_i_hardly_knowadata',
            data = {
                'a' : 'blue',
                'b' : False,
                'c' : None
            }
        )

        # code
        # ...
        # ...

        pass



    # Read methods


    # This method is required

    @classmethod
    def _get_constructor_args(cls,group):
        """
        Generates and returns a dictionary of key:value pairs to pass to
        the class __init__ method.

        Any emdfile class instances which were stored as attributes can be
        retrieved from the .h5 file using cls._get_emd_attr_data(), which
        returns a dictionary of all attribute/instance pairs.

        Metadata dictionaries can be retrieved using emdfile._read_metadata(),
        which returns a single Metadata dict specified by its name.
        """

        # get EMD group data
        emd_data = cls._get_emd_attr_data(cls,group)

        # get metadata dictionaries
        some_metadata = _read_metadata(group,'name')

        # code
        # ...
        # ...

        # make the dictionary of constructor arguments
        constructor_args = {
            'name' : basename(group.name),
            'data' : emd_data['data'].data
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
        Optional. If this method is defined, Custom.to_h5(self,group) should
        be called somewhere inside, to ensure emdfile classes which are instance
        attributes and Metadata dictionaries inside the .metadata property all
        get saved correctly.

        One use of this function is to place any metadata living in
        class attributes into the .metadata such that it will get saved,
        as in the example below
        """
        md = Metadata(
            name = '_attr_metadata',
            data = {
                'Rshape' : self.Rshape,
                'Qshape' : self.Qshape
            }
        )
        self.metadata = md
        Custom.to_h5(self,group)



