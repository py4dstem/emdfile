# emdfile

`emdfile` is an interface for moving data between Python and EMD 1.0 formatted
HDF5 files.  It includes read, write, and append operations.

EMD (Electron Microscopy Dataset) 1.0 is a file specification designed to carry
arbitrary data and metadata.  Data is abstracted into trees and nodes; each
node carries a block of data plus arbitrary metadata.  The full spec is available
[here](https://emdatasets.com/format/). 


## Installation

Run

> pip install emdfile

Or, to install from source code, you can clone this repository and from the
distribution level directory (i.e. where pyproject.toml lives) run

> pip install .


## Examples

For example use-cases, syntax walk-through, and downstream package integration
demo, see the `sample_code` directory.

