from setuptools import setup, find_packages
from distutils.util import convert_path

with open("README.md","r") as f:
    long_description = f.read()

version_ns = {}
vpath = convert_path('emdfile/version.py')
with open(vpath) as version_file:
    exec(version_file.read(), version_ns)

setup(
    name='emdfile',
    version=version_ns['__version__'],
    description='reads and writes EMD 1.0 (HDF5) files',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/py4dstem/emdfile/',
    author='Benjamin H. Savitzky',
    author_email='ben.savitzky@gmail.com',
    license='GNU GPLv3',
    keywords="HDF5",
    python_requires='>=3.7',
    install_requires=[
        'h5py >= 3.2.0',
        'tqdm >= 4.46.1',
        'numpy'
        ],
)

