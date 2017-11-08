# pynumerica

## Overview

pynumerica is a Python package to read MSC URP Radar Numeric data.

## Installation

### Requirements
- Python 3.  Works with Python 2.7
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pynumerica installation.

### Installing pynumerica

```bash
# setup virtualenv
virtualenv --system-site-packages -p python3 pynumerica
cd pynumerica
source bin/activate

# clone codebase and install
git clone https://github.com/ECCC-MSC/pynumerica.git
cd pynumerica
python setup.py build
python setup.py install
```

## Running

```bash
# help
pynumerica --help

# parse a single numerica file
pynumerica -f </path/to/numerica_file>

# add verbose mode (ERROR, WARNING, INFO, DEBUG)
pynumerica -f </path/to/numerica_file> --verbosity=DEBUG
```

### Using the API
```python
from pynumerica import Numeric

# read Numerica data
with open('/path/to/file') as ff:
    n = Numerica(ff)

    for key, value in n.metadata:
        print(key, value)

    print(n.metadata)

    print(n.data)

    print(len(n.data))

    # get the spatial extent
    print(n.get_spatial_extent())

    # get the data extent
    print(n.get_data_extent())


# read Numerica data using convenience functions
# parse file
s = load('/path/to/numerica_file.dat')  # returns Numerica object

# parse data string
with open('/path/to/numerica_file.dat') as ff:
    numerica_string = ff.read()
s = loads(numerica_string)  # returns Numerica object

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
python pynumerica/tests/run_tests.py

# or this:
python setup.py test

# measure code coverage
coverage run --source=pynumerica -m unittest pynumerica.tests.run_tests
coverage report -m
```

## Releasing

```bash
python setup.py sdist bdist_wheel --universal
```

## Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Checking Code for PEP8

```bash
find . -type f -name "*.py" | xargs flake8
```

## Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/pynumerica/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
