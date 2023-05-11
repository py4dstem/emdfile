import emdfile as emd
import numpy as np


# import the classes inheriting from emdfile.
# `sample_custom_emd_classes` must be a python module
# which sets a variable `_emd_hook` to True in its
# toplevel namespace (in this example, in __init__.py)

from sample_custom_emd_classes import (
    SimpleArraySubclass,
    ArraySubclass,
    PointListSubclass,
    PointListArraySubclass,
    #MyCustomClass
)


# set a filepath
filepath = "/Users/Ben/Desktop/test.h5"


# run as a script...
if __name__ == "__main__":

    # instantiate classes
    array1 = SimpleArraySubclass(
        name = 'test_simple_array',
        data = np.zeros((2,2))
    )
    array2 = ArraySubclass(
        name = 'test_array',
        data = np.ones((2,3)),
        color = 'red',
        number = 3,
        elephants = False
    )
    pointlist = PointListSubclass(
        name = 'test_points',
        fields = ['x','y','z'],
        length = 8
    )
    pointlist['x'][1:] = 7
    pointlistarray = PointListArraySubclass(
        name = 'test_pointlistarray',
        shape = (4,5)
    )
    # populate with data
    for (x,y) in np.ndindex((4,5)):
        pointlistarray[x,y] += np.full(x,y,dtype=np.float32)
    # TODO custom

    # save
    emd.save(
        filepath,
        [
            array1,
            array2,
            pointlist,
            pointlistarray,
            #custom_instance
        ],
        mode = 'o'
    )

    # load
    data = emd.read(filepath)

    # display
    print("Loaded data:")
    print(data)
    print()
    print("Loaded tree:")
    data.tree()
    print()
    print("Simple Array subclass:")
    ar = data.tree('test_simple_array')
    print(ar)
    print(ar.name)
    print(ar.data)
    print()
    print("Array subclass with attributes:")
    ar = data.tree('test_array')
    print(ar)
    print(ar.name)
    print(ar.data)
    print(ar.color, ar.number, ar.elephants)
    print()
    print("PointList subclass:")
    pts = data.tree('test_points')
    print(pts)
    print(pts.data)
    print(pts.data.dtype)
    print()
    print("PointListArray subclass:")
    pla = data.tree('test_pointlistarray')
    print(pla)
    print(pla.dtype, pla.fields, pla.types)
    print(pointlistarray[2,3].data)
    print(pla[2,3].data)
    print()
    #print(data.tree('test_custom').data)




