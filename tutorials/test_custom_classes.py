import emdfile as emd

import numpy as np
from os.path import exists
from os import remove

from sample_custom_emd_classes import (
    MyArrayClass,
    MyPointsClass,
    MyCustomClass
)

# set filepath
filepath = "/Users/Ben/Desktop/test.h5"


if __name__ == "__main__":

    # instantiate the test classes
    array_instance = MyArrayClass(
        name = 'test_array_instance',
        data = np.ones((2,3))
    )
    points_instance = MyPointsClass(
        name = 'test_points_instance',
        x = np.arange(10),
        y = np.arange(10,20),
    )
    custom_instance = MyCustomClass(
        name = 'test_custom_instance',
        data = np.arange(12).reshape((3,4))
    )

    # save
    emd.save(
        filepath,
        [array_instance, points_instance, custom_instance],
        mode = 'o'
    )

    # load
    loaded_data = emd.read(filepath)

    # display
    print("Loaded data:")
    print(loaded_data)
    print()
    print("Loaded tree:")
    loaded_data.tree()
    print()
    print("data")
    print(loaded_data.tree('test_array_instance').data)
    print()
    print(loaded_data.tree('test_points_instance').data)
    print()
    print(loaded_data.tree('test_custom_instance').data)




