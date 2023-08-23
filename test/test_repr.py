import emdfile as emd
import numpy as np


def test_array_repr():

    # multidim array
    s = (4,5,6,7)
    ar1 = emd.Array(
        name = 'ar1',
        data = np.arange(np.prod(s)).reshape(s)
    )

    # multidim array with len-2 dim
    s = (2,5,6,7)
    ar2 = emd.Array(
        name = 'ar2',
        data = np.arange(np.prod(s)).reshape(s)
    )

    # multidim array with len-2 dim
    s = (4,2,6,7)
    ar3 = emd.Array(
        name = 'ar3',
        data = np.arange(np.prod(s)).reshape(s)
    )

    # multidim array with len-1 dim
    s = (1,5,6,7)
    ar4 = emd.Array(
        name = 'ar4',
        data = np.arange(np.prod(s)).reshape(s)
    )

    # multidim array with len-1 dim
    s = (4,1,6,7)
    ar5 = emd.Array(
        name = 'ar5',
        data = np.arange(np.prod(s)).reshape(s)
    )

    # single dim array
    ar6 = emd.Array(
        name = 'ar6',
        data = np.arange(10)
    )

    # single dim array, len 2
    ar6 = emd.Array(
        name = 'ar6',
        data = np.arange(2)
    )

    # single dim array, len 1
    ar7 = emd.Array(
        name = 'ar7',
        data = np.arange(1)
    )

    # single dim array, len 0
    ar8 = emd.Array(
        name = 'ar8',
        data = np.arange(0)
    )

    # test __repr__
    print(ar1)
    print(ar2)
    print(ar3)
    print(ar4)
    print(ar5)
    print(ar6)
    print(ar7)
    print(ar8)


