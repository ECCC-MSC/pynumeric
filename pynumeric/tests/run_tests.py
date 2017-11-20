# =================================================================
#
# Copyright (c) 2017 Government of Canada
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =================================================================

from datetime import datetime
import os
import unittest

from pynumeric import __gdal_version__, InvalidDataError, load, loads, Numeric

THISDIR = os.path.dirname(os.path.realpath(__file__))


class NumericTest(unittest.TestCase):
    """Test suite for package pynumeric"""
    def setUp(self):
        """setup test fixtures, etc."""

        pass

    def tearDown(self):
        """return to pristine state"""

        for testfile in ['test.tif', 'test.nc']:
            testfile_ = get_abspath(testfile)
            if os.path.isfile(testfile_):
                os.remove(testfile_)

    def test_gdal(self):
        """test for GDAL support"""

        self.assertIsInstance(__gdal_version__, str)

    def test_numeric(self):
        """test reading numeric files or strings"""

        # test reading a non-numeric file:
        with self.assertRaises(InvalidDataError):
            filename = get_abspath('non-numeric-file.dat')
            with open(filename) as ff:
                n = Numeric(ff)

        filepath = '201611212330:PRECIPET,125,18,MPRATE_QPE,PRECIPET_QC_PARAMETERS_CMC:PRECIPET_NUMERIC_MMHR_WHK'  # noqa

        # test load by file
        filename = get_abspath(filepath)
        n = load(filename)

        # test load by string
        filename = get_abspath(filepath)
        with open(filename) as ff:
            data = ff.read()
            n = loads(data)

        with open(get_abspath(filepath)) as ff:  # noqa
            n = Numeric(ff, filename='test')

            # test core properties
            self.assertEqual(n.filename, 'test')

            # test metadata
            self.assertEqual(n.metadata['MajorProductType'], 'RADAR')
            self.assertEqual(n.metadata['Originator'], 'URP Version 2.9')
            self.assertEqual(n.metadata['MinorProductType'], 'PRECIPET')
            self.assertEqual(n.metadata['ValidTime'],
                             datetime(2016, 11, 21, 23, 30))
            self.assertEqual(n.metadata['LatCentre'], 53.56050)
            self.assertEqual(n.metadata['LonCentre'], -114.14470)
            self.assertEqual(n.metadata['HornHeight'], '17')
            self.assertEqual(n.metadata['Width'], 480)
            self.assertEqual(n.metadata['Height'], 480)

            # test data
            data_spatial_extent = n.get_data_spatial_extent()
            expected = (-116.3552, 52.4903, -113.7049, 54.0015)
            self.assertEqual(expected, data_spatial_extent)

            data_range = n.get_data_range()
            expected = (-0.0099, 0.4211)
            self.assertEqual(expected, data_range)

            self.assertEqual(len(n.data), 407)

    def test_to_grid(self):
        """test writing data to raster grids via GDAL"""

        filepath = '201611212330:PRECIPET,125,18,MPRATE_QPE,PRECIPET_QC_PARAMETERS_CMC:PRECIPET_NUMERIC_MMHR_WHK'  # noqa

        # test load by file
        filename = get_abspath(filepath)
        n = load(filename)

        status = n.to_grid(get_abspath('test.tif'))

        self.assertTrue(status)

        status = n.to_grid(get_abspath('test.nc'), 'NetCDF')

        self.assertTrue(status)


def get_abspath(filepath):
    """helper function absolute file access"""

    return os.path.join(THISDIR, filepath)


if __name__ == '__main__':
    unittest.main()
