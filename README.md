# pynumeric

[![Build Status](https://travis-ci.org/ECCC-MSC/pynumeric.png)](https://travis-ci.org/ECCC-MSC/pynumeric)
[![Coverage Status](https://coveralls.io/repos/github/ECCC-MSC/pynumeric/badge.svg?branch=master)](https://coveralls.io/github/ECCC-MSC/pynumeric?branch=master)

## Overview

pynumeric is a Python package to read [MSC Radar Numeric data](http://collaboration.cmc.ec.gc.ca/cmc/CMOI/produits/samples/radar/vscan/Radar_Products_Available_CMC_Mai_2015_external.pdf).

## Installation

The easiest way to install pynumeric is via the Python [pip](https://pip.pypa.io/en/stable/)
utility:

```bash
pip install pynumeric
```

### Requirements
- Python 3.  Works with Python 2.7
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pynumeric installation.

### Installing pynumeric

```bash
# setup virtualenv
virtualenv --system-site-packages -p python3 pynumeric
cd pynumeric
source bin/activate

# clone codebase and install
git clone https://github.com/ECCC-MSC/pynumeric.git
cd pynumeric
python setup.py build
python setup.py install
```

## Running

```bash
# help
pynumeric --help

# get pynumeric version
pynumeric --version

# get pynumeric GDAL version
pynumeric --gdal-version

# report on a single numeric file
pynumeric report -f </path/to/numeric_file>

# add verbose mode (ERROR, WARNING, INFO, DEBUG)
pynumeric report -f </path/to/numeric_file> --verbosity=DEBUG

# export a numeric file to GeoTIFF
pynumeric export -f </path/to/numeric_file> -o foo.tif -of GTiff

# export a numeric file to NetCDF
pynumeric export -f </path/to/numeric_file> -o foo.tif -of NetCDF

```

### Using the API
```python
from pynumeric import Numeric

# read Numeric data
with open('/path/to/file') as ff:
    n = Numeric(ff)

    for key, value in n.metadata:
        print(key, value)

    print(n.metadata)

    print(n.data)

    print(len(n.data))

    # get the spatial extent
    print(n.get_spatial_extent())

    # get the data extent
    print(n.get_data_extent())


# read Numeric data using convenience functions
# parse file
s = load('/path/to/numeric_file.dat')  # returns Numeric object

# parse data string
with open('/path/to/numeric_file.dat') as ff:
    numeric_string = ff.read()
s = loads(numeric_string)  # returns Numeric object

# export to GeoTIFF
# Supported are any of the supported GDAL
# Raster Format Codes (http://www.gdal.org/formats_list.html)
s.to_grid('myfile.tif', 'GTiff')  # creates myfile.tif on disk
```

## Development

```bash
pip install requirements-dev.txt
```
### Running Tests

```bash
# install dev requirements
pip install -r requirements-dev.txt

# run tests like this:
python pynumeric/tests/run_tests.py

# or this:
python setup.py test

# measure code coverage like this
coverage run --source=pynumeric -m unittest pynumeric.tests.run_tests
coverage report -m

# or this:
python setup.py coverage
```

## Releasing

```bash
python setup.py sdist bdist_wheel --universal
twine upload dist/*
```

## Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Checking Code for PEP8

```bash
find . -type f -name "*.py" | xargs flake8
```

## Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/pynumeric/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
