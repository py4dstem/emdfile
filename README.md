# emdfile

EMD (Electron Microscopy Dataset) 1.0 is an HDF5 based file format which
is designed to carry arbitrary data and metadata.  An overview of the
file specification can be found [here](https://emdatasets.com/format/).


`emdfile` is a Python package defining write and read functions and a set of
classes which together interface between EMD 1.0 files and Python runtime
objects.  The classes are designed to quickly build, save to, and read from
filetree-like representations of data and metadata, and is built on HDF5+h5py.


## Installation

Run

> pip install emdfile

Or, to install from source code, you can clone this repository and from the
distribution level directory (i.e. where pyproject.toml lives) run

> pip install .



## Examples and syntax


For a few simple examples...
(([this is coming extremely soon ish!](https://www.youtube.com/watch?v=ebeNeQFUMa0)))

For a longer, narrative intro example, see
[tutorials/emd_intro_example.ipynb](https://github.com/py4dstem/emdfile/blob/main/tutorials/emdfile_intro_example.ipynb).

For a detailed walkthrough of the syntax, see
[tutorials/emd_package_walkthrough.ipynb](https://github.com/py4dstem/emdfile/blob/main/tutorials/emdfile_package_walkthrough.ipynb).


`emdfile` is designed to support I/O in downstream Python modules and packages.
When [tutorials/test_custom_classes.py](https://github.com/py4dstem/emdfile/blob/main/tutorials/test_custom_classes.py) is run as a script, it makes, saves, loads, then prints the contents of the data carrying classes defined in the [tutorials/sample_custom_emd_classes](https://github.com/py4dstem/emdfile/tree/main/tutorials/sample_custom_emd_classes) Python module.





