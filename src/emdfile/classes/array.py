import h5py
import numpy as np
from typing import Optional,Union
from numbers import Number
from os.path import basename
from emdfile.classes.node import Node

class Array(Node):
    """
    Array instances store N-dimensional array-like data.

    Instantiation
    -------------
    For some numpy array x

    >>> ar = Array( x )

    creates an Array instance.  Calibrations may be passed on instantion

    >>> ar = Array(
    >>>     np.ones((20,20,256,256)),
    >>>     name = '4ddatacube',
    >>>     units = 'intensity',
    >>>     dims = [
    >>>         [0,5],
    >>>         [0,5],
    >>>         [0,0.01],
    >>>         [0,0.01]
    >>>     ],
    >>>     dim_units = [
    >>>         'nm',
    >>>         'nm',
    >>>         'A^-1',
    >>>         'A^-1'
    >>>     ],
    >>>     dim_names = [
    >>>         'rx',
    >>>         'ry',
    >>>         'qx',
    >>>         'qy'
    >>>     ],
    >>> )

    "Stack-arrays" are constructed by passing the `slicelables` argument

    >>> ar = Array(
    >>>     np.ones((4,50,50)),
    >>>     name = 'test_array_stack',
    >>>     units = 'intensity',
    >>>     dims = [
    >>>         [0,2],
    >>>         [0,2]
    >>>     ],
    >>>     dim_units = [
    >>>         'nm',
    >>>         'nm'
    >>>     ],
    >>>     dim_names = [
    >>>         'rx',
    >>>         'ry'
    >>>     ],
    >>>     slicelabels = [
    >>>         'a',
    >>>         'b',
    >>>         'c',
    >>>         'd'
    >>>     ]
    >>> )

    representing a set of M arrays, each of shape N-1 all calibrated by one set
    of object calibrations, given Array shape N and initial dimension extent M.
    Above, M is 4 and the arrays are called 'a', 'b', 'c', 'd'.

    The `dims` argument calibrates the array axes. Constant pixel sizes may
    be specified as length 2 lists, which will extrapolate linearly. For non-
    linear pixel extents an array of the dim length should be specified, e.g.

    >>> x = np.logspace(0,1,100)
    >>> y = np.sin(x)
    >>> ar = Array(
    >>>     y,
    >>>     dims = [
    >>>         x
    >>>     ]
    >>> )

    Data Access
    -----------
    For an Array instance ar, data can be accessed as

        >>> ar.data

    or can be accessed using numpy-like slicing into the object itself, e.g.

        >>> ar[:]

    For stack-arrays, a slice called 'a' can be retrieved with

        >>> ar['a']

    Dimension Vectors
    -----------------
    The set of all dim vectors can be retrieved with

        >>> ar.dims

    and the n'th dim vector with

        >>> ar.get_dim(n)

    Dim vectors should be modified using

        >>> ar.set_dim

    to write a new dimension vector or

        >>> ar.set_dim_units
        >>> ar.set_dim_name

    to modify dim vector metadata only.

    Shape Information
    -----------------
    Shape information is accessible as normal through

        >>> ar.data.shape

    Additionally, the following shape properties account for stack arrays

        >>> ar.depth    # 0 for non stacks; # arrays for stacks
        >>> ar.rank     # N for non stacks; N-1 for stacks
        >>> ar.shape    # length N for non stacks; length N-1 for stacks
    """
    _emd_group_type = 'array'
    def __init__(
        self,
        data: np.ndarray,
        name: Optional[str] = 'array',
        units: Optional[str] = '',
        dims: Optional[list] = None,
        dim_names: Optional[list] = None,
        dim_units: Optional[list] = None,
        slicelabels = None
        ):
        """
        Parameters
        ----------
        data : np.ndarray
        name : str
        units : str
            units for the pixel values
        dims : variable
            calibration vectors for each axis of the data
            array.  Valid values for each element of the list are None,
            a number, a 2-element list/array, or an M-element list/array
            where M is the data array.  If None is passed, the dim will be
            populated with integer values starting at 0 and its units will
            be set to pixels.  If a number is passed, the dim is populated
            with a vector beginning at zero and increasing linearly by this
            step size.  If a 2-element list/array is passed, the dim is
            populated with a linear vector with these two numbers as the first
            two elements.  If a list/array of length M is passed, this is used
            as the dim vector, (and must therefore match this dimension's
            length). If dims recieves a list of fewer than N arguments for an
            N-dimensional data array, the extra dimensions are populated as if
            None were passed, using integer pixel values. If the `dims`
            parameter is not passed, all dim vectors are populated this way.
        dim_units : list
            the units for the calibration dim vectors. If
            nothing is passed, dims vectors which have been populated
            automatically with integers corresponding to pixel numbers
            will be assigned units of 'pixels', and any other dim vectors
            will be assigned units of 'unknown'.  If a list with length <
            the array dimensions, the passed values are assumed to apply
            to the first N dimensions, and the remaining values are
            populated with 'pixels' or 'unknown' as above.
        dim_names : list
            labels for each axis of the data array. Values
            which are not passed, following the same logic as described
            above, will be autopopulated with the name "dim#" where #
            is the axis number.
        slicelabels : None or True or list
            if not None, array will be promoted to a stack array - see object
            docstring for details. If a list is passed it should specify the
            sub-array names.

        Returns
        -------
        A new Array instance
        """
        # instantiate as a None
        super().__init__()

        # populate
        self.data = data
        self.name = name
        self.units = units

        # For array stacks, setup shape and labels
        if slicelabels is None:
            self.is_stack = False
            self.slicelabels = None
        else:
            self.is_stack = True
            # Populate labels
            if slicelabels is True:
                slicelabels = [f'array{i}' for i in range(self.depth)]
            elif len(slicelabels) < self.depth:
                slicelabels = np.concatenate((slicelabels,
                    [f'array{i}' for i in range(len(slicelabels),self.depth)]))
            else:
                slicelabels = slicelabels[:self.depth]
            self.slicelabels = Labels(slicelabels)

        # dim vectors

        # set initial state
        self._dims = tuple([None for i in range(self.rank)])
        self._dim_units = tuple(['unknown' for i in range(self.rank)])
        self._dim_names = tuple([f"dim{i}" for i in range(self.rank)])
        # expand dims, dim_units, and dim_names to lists of length = rank,
        # padding with None if the lists are too short
        if dims is None:
            dims = [None for i in range(self.rank)]
        else:
            assert(isinstance(dims,(list,tuple))), f"dims must be None or a list or tuple, not type {type(dims)}"
            if len(dims) < (self.rank):
                dims = list(dims) + [None for i in range(self.rank-len(dims))]
            else:
                dims = dims[:self.rank]
        # set flag for if units are pixels
        dim_in_pixels = np.zeros(self.rank, dtype=bool)
        for idx in range(self.rank):
            dim_in_pixels[idx] = dims[idx] is None
        # dim units 
        if dim_units is None:
            dim_units = ['unknown' for i in range(self.rank)]
        else:
            assert(isinstance(dim_units,(list,tuple))), f"dim_units must be None or a list or tuple, not type {type(dim_units)}"
            if len(dim_units) < (self.rank):
                dim_units = list(dim_units) + ['unknown' for i in range(self.rank-len(dim_units))]
            else:
                dim_units = dim_units[:self.rank]
        dim_units = np.array(dim_units)
        dim_units[dim_in_pixels] = 'pixels'
        dim_units = tuple(dim_units)
        # dim names
        if dim_names is None:
            dim_names = [f"dim{i}" for i in range(self.rank)]
        else:
            assert(isinstance(dim_names,(list,tuple))), f"dim_names must be None or a list or tuple, not type {type(dim_names)}"
            if len(dim_names) < (self.rank):
                dim_names = list(dim_names) + [f"dim{i+len(dim_names)}" for i in range(self.rank-len(dim_names))]
            else:
                dim_names = dim_names[:self.rank]
        # set the dims
        for idx,(d,du,dn) in enumerate(zip(dims,dim_units,dim_names)):
            self.set_dim(
                idx,
                dim = d,
                units = du,
                name = dn
            )

    # dim vector setter/getter properties and methods
    @property
    def dims(self):
        return self._dims
    def get_dim(self,n):
        """ Return the n'th dim vector
        """
        assert(isinstance(n,(int,np.integer))), f"Can't retrieve the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't retrieve the {n}th dim vector - {n} must be < {self.rank}"
        return self.dims[n]
    # alias
    dim = get_dim
    def set_dim(
        self,
        n:int,
        dim:Union[list,np.ndarray],
        units:Optional[str]=None,
        name:Optional[str]=None
        ):
        """
        Sets the n'th dim vector, using `dim` as described in the Array
        documentation. If `units` and/or `name` are passed, sets these
        values for the n'th dim vector.

        Parameters
        ----------
        n : int
            specifies which dim vector
        dim : list or array
            length must be either 2, or match the length of the n'th axis
        units : str
        name : str
        """
        assert(isinstance(n,(int,np.integer))), f"Can't set the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't set the {n}th dim vector - {n} must be < {self.rank}"
        length = self.shape[n]
        # unpack dim, if a number or len 2 list were passed
        new_dim = self._unpack_dim(dim,length)
        # set new dim
        self._dims = list(self._dims)
        self._dims[n] = new_dim
        self._dims = tuple(self._dims)
        if units is not None:
            self.set_dim_units(n,units)
        if name is not None:
            self.set_dim_name(n,name)

    @property
    def dim_units(self):
        return self._dim_units
    def get_dim_units(self,n):
        """ Return the n'th dim vector units
        """
        assert(isinstance(n,(int,np.integer))), f"Can't retrieve the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't retrieve the {n}th dim vector - {n} must be < {self.rank}"
        return self.dim_units[n]
    def set_dim_units(
        self,
        n:int,
        units:str,
        ):
        """
        Sets the n'th dim vector units to `units`.

        Parameters
        ----------
        n : int
            which dim vector
        units : str
            new units
        """
        assert(isinstance(n,(int,np.integer))), f"Can't set the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't set the {n}th dim vector - {n} must be < {self.rank}"
        self._dim_units = list(self._dim_units)
        self._dim_units[n] = units
        self._dim_units = tuple(self._dim_units)

    @property
    def dim_names(self):
        return self._dim_names
    def get_dim_name(self,n):
        """ Get the n'th dim vector name
        """
        assert(isinstance(n,(int,np.integer))), f"Can't retrieve the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't retrieve the {n}th dim vector - {n} must be < {self.rank}"
        return self.dim_names[n]
    def set_dim_name(
        self,
        n:int,
        name:str,
        ):
        """
        Sets the n'th dim vector name to `name`.

        Parameters
        ----------
        n : int
            which dim vector
        name : str
            new name
        """
        assert(isinstance(n,(int,np.integer))), f"Can't set the {n}th dim vector - {n} must be an integer, not type {type(n)}."
        assert(n < self.rank), f"Can't set the {n}th dim vector - {n} must be < {self.rank}"
        self._dim_names = list(self._dim_names)
        self._dim_names[n] = name
        self._dim_names = tuple(self._dim_names)

    @staticmethod
    def _unpack_dim(dim,length):
        """
        Given a dim vector as passed at instantiation and the expected length
        of this dimension of the array, this function checks the passed dim
        vector length, and checks the dim vector type.  For number-like dim-
        vectors:
            -if it is a number, turns it into the list [0,number] and proceeds
                as below
            -if it has length 2, linearly extends the vector to its full length
            -if it has length `length`, returns the vector as is
            -if it has any other length, raises an Exception.

        For string-like dim vectors, the length must match the array dimension
        length.

        Accepts:
            dim (list or array)
            length (int)

        Returns
            the unpacked dim vector
        """
        # Expand None
        if dim is None:
            dim = 1
        # Expand single numbers
        if isinstance(dim,Number):
            dim = [0,dim]
        N = len(dim)
        # for string dimensions (used for stack arrays):
        if not isinstance(dim[0],Number):
            assert(N == length), f"For non-numerical dims, the dim vector length must match the array dimension length. Recieved a dim vector of length {N} for an array dimension length of {length}."
        # For number-like dimensions:
        if N == length:
            return dim
        elif N == 2:
            start,step = dim[0],dim[1]-dim[0]
            stop = start + step*length
            return np.arange(start,stop,step)
        else:
            raise Exception(f"dim vector length must be either 2 or equal to the length of the corresponding array dimension; dim vector length was {dim} and the array dimension length was {length}")

    def _dim_is_linear(self,dim,length):
        """
        Returns True if a dim is linear, else returns False
        """
        try:
            dim_expanded = self._unpack_dim(dim[:2],length)
            return np.array_equal(dim,dim_expanded)
        except IndexError:
            return True

    # Shape properties
    @property
    def shape(self):
        if not self.is_stack:
            return self.data.shape
        else:
            return self.data.shape[1:]
    @property
    def depth(self):
        if not self.is_stack:
            return 0
        else:
            return self.data.shape[0]
    @property
    def rank(self):
        if not self.is_stack:
            return self.data.ndim
        else:
            return self.data.ndim - 1

    ## Slicing
    def get_slice(self,label,name=None):
        idx = self.slicelabels._dict[label]
        return Array(
            data = self.data[idx],
            name = name if name is not None else self.name+'_'+label,
            units = self.units,
            dims = self.dims,
            dim_units = self.dim_units,
            dim_names = self.dim_names
        )
    def __getitem__(self,x):
        if isinstance(x,str):
            return self.get_slice(x)
        elif isinstance(x,tuple) and isinstance(x[0],str):
            return self.get_slice(x[0])[x[1:]]
        else:
            return self.data[x]

    ## Representation to standard output
    def __repr__(self):
        if not self.is_stack:
            space = ' '*len(self.__class__.__name__)+'  '
            string = f"{self.__class__.__name__}( A {self.rank}-dimensional array of shape {self.shape} called '{self.name}',"
            string += "\n"+space+"with dimensions:"
            string += "\n"
        else:
            space = ' '*len(self.__class__.__name__)+'  '
            string = f"{self.__class__.__name__}( A stack of {self.depth} Arrays with {self.rank}-dimensions and shape {self.shape}, called '{self.name}'"
            string += "\n"
            string += "\n" +space + "The labels are:"
            for label in self.slicelabels:
                string += "\n" + space + f"    {label}"
            string += "\n"
            string += "\n"
            string += "\n" + space + "The Array dimensions are:"
        for n in range(self.rank):
            if len(self.dims[n]) >= 3:
                string += "\n"+space+f"    {self.dim_names[n]} = [{self.dims[n][0]},{self.dims[n][1]},{self.dims[n][2]},...] {self.dim_units[n]}"
            elif len(self.dims[n]) == 2:
                string += "\n"+space+f"    {self.dim_names[n]} = [{self.dims[n][0]},{self.dims[n][1]}] {self.dim_units[n]}"
            elif len(self.dims[n]) == 1:
                try:
                    string += "\n"+space+f"    {self.dim_names[n]} = [{self.dims[n][0]}] {self.dim_units[n]}"
                except(IndexError):
                    string += "\n"+space+f"    {self.dim_names[n]} = [{self.dims[n][:]}] {self.dim_units[n]}"
            else:
                try:
                    string += "\n"+space+f"    {self.dim_names[n]} = [] {self.dim_units[n]}"
                except(IndexError):
                    string += "\n"+space+f"    {self.dim_names[n]} = [{self.dims[n][:]}] {self.dim_units[n]}"
            if not self._dim_is_linear(self.dims[n],self.shape[n]):
                string += "  (*non-linear*)"
        string += "\n)"
        return string

    # HDF5 read/write
    # write
    def to_h5(self,group):
        """
        Calls Node.to_h5 to greate the group's node and write its metadata.
        Then writes Array data, calibration vectors, units, and any stack/label
        info.

        Parameters
        ----------
        group : h5py Group

        Returns
        -------
        (h5py Group) the new array's Group
        """
        # Construct group and add metadata
        grp = Node.to_h5(self,group)

        # add the data
        data = grp.create_dataset(
            "data",
            shape = self.data.shape,
            data = self.data
            #dtype = type(self.data)
        )
        data.attrs.create('units',self.units) # save 'units' but not 'name' - 'name' is the group name

        # Add the normal dim vectors
        for n in range(self.rank):
            # unpack info
            dim = self.dims[n]
            name = self.dim_names[n]
            units = self.dim_units[n]
            # compress the dim vector if it's linear
            if self._dim_is_linear(dim,self.shape[n]):
                dim = dim[:2]
            # write
            dset = grp.create_dataset(
                f"dim{n}",
                data = dim
            )
            dset.attrs.create('name',str(name))
            dset.attrs.create('units',str(units))

        # Add stack dim vector, if present
        if self.is_stack:
            n = self.rank
            dim = [s.encode('utf-8') for s in self.slicelabels]
            # write
            dset = grp.create_dataset(
                f"dim{n}",
                data = dim
            )
            dset.attrs.create('name','_labels_')

        # return
        return grp

    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Takes an h5py Group corresponding to some EMD node, and returns a
        dictionary of arguments/values to pass to the corresponding class
        constructor.
        """
        # get data
        dset = group['data']
        data = dset[:]
        units = dset.attrs['units']
        rank = len(data.shape)

        # determine if this is a stack array
        last_dim = group[f"dim{rank-1}"]
        if last_dim.attrs['name'] == '_labels_':
            is_stack = True
            normal_dims = rank-1
        else:
            is_stack = False
            normal_dims = rank

        # get dim vectors
        dims = []
        dim_units = []
        dim_names = []
        for n in range(normal_dims):
            dim_dset = group[f"dim{n}"]
            dims.append(dim_dset[:])
            dim_units.append(dim_dset.attrs['units'])
            dim_names.append(dim_dset.attrs['name'])

        # if it's a stack array, get the labels
        if is_stack:
            slicelabels = last_dim[:]
            slicelabels = [s.decode('utf-8') for s in slicelabels]
        else:
            slicelabels = None

        # make args dictionary and return
        return {
            'data' : data,
            'name' : basename(group.name),
            'units' : units,
            'dims' : dims,
            'dim_names' : dim_names,
            'dim_units' : dim_units,
            'slicelabels' : slicelabels
        }

# List subclass for accessing data slices with a dict
class Labels(list):

    def __init__(self,x=[]):
        list.__init__(self,x)
        self.setup_labels_dict()

    def __setitem__(self,idx,label):
        label_old = self[idx]
        del(self._dict[label_old])
        list.__setitem__(self,idx,label)
        self._dict[label] = idx

    def setup_labels_dict(self):
        self._dict = {}
        for idx,label in enumerate(self):
            self._dict[label] = idx
