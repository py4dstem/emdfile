import h5py
import numpy as np
from typing import Optional
from os.path import basename
from emdfile.tqdmnd import tqdmnd
from emdfile.classes.node import Node
from emdfile.classes.pointlist import PointList

class PointListArray(Node):
    """
    A PointListArray instance comprises a 2D grid of PointLists, each sharing a
    single dtype and set of fields, and each having any variable length. It
    therefore represents a "ragged array" in 2+1 dimensions, i.e. with two
    dimensions of a fixed shape and one of variable length, embedded in an
    M dimensional space for PointLists with M fields.

    .. topic:: Instantiation

        Calling

            >>> pla = PointListArray(
            >>>     [('a',float),('b',float)],
            >>>     (5,5)
            >>> )

        will create a 5x5 PointListArray instance with fields 'a' and 'b', and

            >>> dt = np.dtype([('a',float,('b',float)])
            >>> for x in range(5):
            >>>     for y in range(5):
            >>>         pla[x,y] += np.zeros(x+y,dt)

        will populate it with some data. Element assignment currently may only be
        made to PointLists, so using direct assignment the code above must be

            >>> dt = np.dtype([('a',float,('b',float)])
            >>> for x in range(5):
            >>>     for y in range(5):
            >>>         pla[x,y] = PointList(np.zeros(x+y,dt))

    .. topic:: Attributes & Methods

        PointListArrays include attributes

            >>> pla.shape
            >>> pla.dtype
            >>> pla.fields

        and methods

            >>> pla.copy        # returns a copy
            >>> pla.add_fields  # returns a copy with additional fields
    """
    _emd_group_type = "pointlistarray"
    def __init__(
        self,
        dtype,
        shape,
        name: Optional[str] = 'pointlistarray',
        ):
        """
		Creates an empty PointListArray.

        Parameters
        ----------
        dtype : dtype
            the dtype of the data comprising each PointList
        shape : 2-tuple of ints
            the shape of the array of PointLists
        name : str

        Returns
        -------
        (PointListArray)
        """
        super().__init__()
        assert len(shape) == 2, "Shape must have length 2."
        self.name = name
        self.shape = shape
        self.dtype = np.dtype(dtype)
        self.fields = self.dtype.names
        if self.fields is not None:
            self.types = tuple([self.dtype.fields[f][0] for f in self.fields])
        else:
            self.fields = ('',)
            self.types = (dtype,)

        # Populate with empty PointLists
        self._pointlists = [[PointList(data=np.zeros(0,dtype=self.dtype), name=f"{i},{j}")
                             for j in range(self.shape[1])] for i in range(self.shape[0])]

    ## get/set pointlists
    def __getitem__(self, tup):
        l = len(tup) if isinstance(tup,tuple) else 1
        assert(l==2), f"Expected 2 slice values, recieved {l}"
        return self.get_pointlist(tup[0],tup[1])
    def __setitem__(self, tup, pointlist):
        l = len(tup) if isinstance(tup,tuple) else 1
        assert(l==2), f"Expected 2 slice values, recieved {l}"
        assert(pointlist.fields == self.fields), "fields must match"
        self._pointlists[tup[0]][tup[1]] = pointlist
    def get_pointlist(self, i, j, name=None):
        """
        Returns the pointlist at i,j
        """
        pl = self._pointlists[i][j]
        if name is not None:
            pl = pl.copy(name=name)
        return pl

    ## Make copies
    def copy(self, name=''):
        """
        Returns a copy of itself.
        """
        new_pla = PointListArray(
            dtype=self.dtype,
            shape=self.shape,
            name=name)
        for i in range(new_pla.shape[0]):
            for j in range(new_pla.shape[1]):
                pl = new_pla.get_pointlist(i,j)
                pl.add(np.copy(self.get_pointlist(i,j).data))
        for k,v in self.metadata.items():
            new_pla.metadata = v.copy(name=k)
        return new_pla

    def add_fields(self, new_fields, name=''):
        """
        Creates a copy of the PointListArray, but with additional fields given
        by new_fields.

        Parameters
        ----------
        new_fields : list of 2-tuples, ('name', dtype)
        name : string
        """
        dtype = []
        for f,t in zip(self.fields,self.types):
            dtype.append((f,t))
        for f,t in new_fields:
            dtype.append((f,t))
        new_pla = PointListArray(
            dtype=dtype,
            shape=self.shape,
            name=name)
        for i in range(new_pla.shape[0]):
            for j in range(new_pla.shape[1]):
                # Copy old data into a new structured array
                pl_old = self.get_pointlist(i,j)
                data = np.zeros(pl_old.length, np.dtype(dtype))
                for f in self.fields:
                    data[f] = np.copy(pl_old.data[f])
                # Write into new pointlist
                pl_new = new_pla.get_pointlist(i,j)
                pl_new.add(data)
        return new_pla

    ## Representation to standard output
    def __repr__(self):
        space = ' '*len(self.__class__.__name__)+'  '
        string = f"{self.__class__.__name__}( A shape {self.shape} PointListArray called '{self.name}',"
        string += "\n"+space+f"with {len(self.fields)} fields:"
        string += "\n"
        space2 = max([len(field) for field in self.fields])+3
        for f,t in zip(self.fields,self.types):
            string += "\n"+space+f"{f}{(space2-len(f))*' '}({str(t)})"
        string += "\n)"
        return string

    # HDF5 i/o
    # write
    def to_h5(self,group):
        """
        Calls Node.to_h5 to greate the group's node and write its metadata.
        Then writes PointListArray data including the data itself, array shape
        and the dtype.

        Parameters
        ----------
        group : h5py Group

        Returns
        -------
        (h5py Group) the new pointlistarray's group
        """
        # Construct group and add metadata
        grp = Node.to_h5(self,group)
        # Add metadata
        dtype = h5py.special_dtype(vlen=self.dtype)
        dset = grp.create_dataset(
            "data",
            self.shape,
            dtype
        )
        # Add data
        for (i,j) in tqdmnd(dset.shape[0],dset.shape[1]):
            dset[i,j] = self[i,j].data
        # Return
        return grp

    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Takes an h5py Group corresponding to some EMD node, and returns a
        dictionary of arguments/values to pass to the corresponding class
        constructor.
        """
        # Get the DataSet
        dset = group['data']
        dtype = h5py.check_vlen_dtype( dset.dtype )
        shape = dset.shape
        # make args dictionary and return
        return {
            'dtype' : dtype,
            'shape' : shape,
            'name' : basename(group.name)
        }
        # Add metadata
        _read_metadata(pla, group)
        return pla

    def _populate_instance(self,group):
        """
        Accepts an already extant class self, and populates it with the data from h5py Group `group`
        """
        # Find the data and shape
        dset = group['data']
        shape = self.shape
        # Add data
        for (i,j) in tqdmnd(shape[0],shape[1],desc="Reading PointListArray",unit="PointList"):
            try:
                self[i,j].add(dset[i,j])
            except ValueError:
                pass
        return self

