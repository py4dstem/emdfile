# emdfile

EMD (Electron Microscopy Dataset) 1.0 is an HDF5 based file format which
is designed to carry arbitrary data and metadata.  An overview of the
file specification can be found [here](https://emdatasets.com/format/).


`emdfile` is a Python package defining write and read functions and a set of
classes which together interface between EMD 1.0 files and Python runtime
objects.  The classes are designed to quickly build, save to, and read from
filetree-like representations of data and metadata.


## Installation

Run

> pip install emdfile

Or, to install from source code, clone this repository and from the
distribution level directory (i.e. where pyproject.toml lives) run

> pip install .



## Examples and syntax

For a narrative introduction, see
[tutorials/emd_narrative_intro.md](tutorials/emd_narrative_intro.md).

For an example, see
[tutorials/emd_intro_example.ipynb](./tutorials/emd_intro_example.ipynb).

For an walkthrough of the syntax, see
[tutorials/emd_package_walkthrough.ipynb](./tutorials/emd_package_walkthrough.ipynb).

For an example of a downstream Python package using emdfile for IO, see
[tutorials/test_custom_class.py](./tutorials/test_custom_class.py) and
[tutorials/sample_custom_class_module](./tutorials/sample_custom_class_module).





