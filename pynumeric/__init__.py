# -*- coding: utf-8 -*-
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

from collections import OrderedDict
from datetime import datetime
import logging
import os

try:
    from osgeo import gdal, ogr, osr
    __gdal_version__ = gdal.__version__
except ImportError:
    __gdal_version__ = None

from six import StringIO

import click

__version__ = '0.1.2'

LOGGER = logging.getLogger(__name__)


class Numeric(object):
    """MSC URP Numeric object model"""

    def __init__(self, ioobj=None, filename=None):
        """
        Initialize a Numeric object

        :param iooobj: file or StringIO object
        :param filename: filename (optional)

        :returns: pynumeric.Numeric instance
        """

        self.filename = filename
        """filename (optional)"""

        self.metadata = OrderedDict()
        """metadata fields"""

        self.data = []
        """data fields"""

        if filename is not None:
            self.filename = os.path.basename(filename)

        filelines = ioobj.readlines()

        LOGGER.debug('Detecting if file is a Numeric file')
        is_numeric = [s for s in filelines if 'MajorProductType RADAR' in s]
        if not is_numeric:
            raise InvalidDataError('Unable to detect Numeric format')

        LOGGER.debug('Parsing lines')
        for line in filelines:
            try:
                key, value = [s.strip() for s in line.split(' ', 1)]
            except ValueError:
                LOGGER.error('Malformed line: {}'.format(line))
            if key in ['Width', 'Height']:
                LOGGER.debug('Casting {} as int'.format(value))
                self.metadata[key] = int(value)
            elif key in ['LatCentre', 'LonCentre', 'LatitudeIncrement',
                         'LongitudeIncrement']:
                LOGGER.debug('Casting {} as float'.format(value))
                self.metadata[key] = float(value)
            elif key == 'ValidTime':
                LOGGER.debug('Casting {} as datetime'.format(value))
                self.metadata[key] = datetime.strptime(value, '%Y%m%d%H%M')
            elif key == 'Data':  # split into list of tuples (lat, long, value)
                LOGGER.debug('Parsing data values')
                n = 3
                v = value.split(',')
                data = [','.join(v[i:i+n]) for i in range(0, len(v), n)]

                for d in data:
                    self.data.append([float(i) for i in d.split(',')])
            else:
                LOGGER.debug('Casting {} as string'.format(value))
                self.metadata[key] = value

    def get_data_spatial_extent(self):
        """returns tuple of minx, miny, maxx, maxy"""

        latitudes = sorted([i[0] for i in self.data])
        longitudes = sorted([i[1] for i in self.data])

        return (longitudes[0], latitudes[0], longitudes[-1], latitudes[-1])

    def get_data_range(self):
        """returns tuple min/max of data values"""

        data_values = sorted([i[2] for i in self.data])

        return (data_values[0], data_values[-1])

    def to_grid(self, filename='out.tif', fmt='GTiff'):
        """
        transform numeric data into raster grid

        :param filename: filename of output file
        :param fmt: file format.  Supported are any of the supported GDAL
                    Raster Format Codes (http://www.gdal.org/formats_list.html)

        :returns: boolean (file saved on disk)
        """

        if __gdal_version__ is None:
            raise RuntimeError('GDAL Python package is required')

        LOGGER.debug('Creating OGR vector layer in memory')
        vsource = ogr.GetDriverByName('MEMORY').CreateDataSource('memory')

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        vlayer = vsource.CreateLayer('memory', srs, ogr.wkbPoint)

        vlayer.CreateField(ogr.FieldDefn('value', ogr.OFTReal))

        for d in self.data:
            vfeature = ogr.Feature(vlayer.GetLayerDefn())
            vfeature.SetField('value', d[2])

            # create the WKT for the feature using Python string formatting
            wkt = 'POINT(%f %f)' % (d[1], d[0])

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            vfeature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            vlayer.CreateFeature(vfeature)
            # Dereference the feature
            vfeature = None

        LOGGER.debug('Creating GDAL raster layer')
        width = self.metadata['Width']
        height = self.metadata['Height']
        resx = self.metadata['LongitudeIncrement']
        resy = self.metadata['LatitudeIncrement']

        minx = ((self.metadata['LonCentre'] - resx * (width / 2)) - (resx / 2))

        maxy = ((self.metadata['LatCentre'] + resy * (height / 2)) -
                (resy / 2))

        dsource = gdal.GetDriverByName(str(fmt)).Create(filename, width,
                                                        height, 1,
                                                        gdal.GDT_Float64)

        dsource.SetProjection(srs.ExportToWkt())

        dsource.SetGeoTransform((minx, resx, 0.0, maxy, 0.0, -resy))
        dband = dsource.GetRasterBand(1)
        dband.SetNoDataValue(-9999)

        LOGGER.debug('Rastering virtual vector data')
        gdal.RasterizeLayer(dsource, [1], vlayer, options=['ATTRIBUTE=value'])
        LOGGER.info('Filename {} saved to disk'.format(filename))

        LOGGER.debug('Freeing data sources')
        vsource = None
        dsource = None

        return True


class InvalidDataError(Exception):
    """Exception stub for format reading errors"""
    pass


def load(filename):
    """
    Parse Numeric data from from file
    :param filename: filename
    :returns: pynumeric.Numeric object
    """

    with open(filename) as ff:
        return Numeric(ff, filename=filename)


def loads(strbuf):
    """
    Parse Numeric data from string
    :param strbuf: string representation of Numeric data
    :returns: pynumeric.Numeric object
    """

    s = StringIO(strbuf)
    return Numeric(s)


def gdal_version_callback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__gdal_version__)
    ctx.exit()


@click.group()
@click.version_option(version=__version__)
@click.option('--gdal-version', is_flag=True, is_eager=True,
              callback=gdal_version_callback,
              help='Show the GDAL version and exit.')
def cli(gdal_version):
    if gdal_version:
        click.echo(__gdal_version__)
    pass


@click.command()
@click.pass_context
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to Numeric data file')
@click.option('--verbosity', type=click.Choice(['ERROR', 'WARNING',
              'INFO', 'DEBUG']), help='Verbosity')
def report(ctx, file_, verbosity):
    """parse Numeric data files"""

    if verbosity is not None:
        logging.basicConfig(level=getattr(logging, verbosity))
    else:
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    if file_ is None:
        raise click.ClickException('Missing argument')

    with open(file_) as fh:
        try:
            n = Numeric(fh, filename=file_)
            click.echo('Numeric file: {}\n'.format(n.filename))
            click.echo('Metadata:')
            for key, value in n.metadata.items():
                click.echo(' {}: {}'.format(key, value))
            click.echo('\nData:')
            click.echo(' Number of records: {}'.format(len(n.data)))
            click.echo(' Spatial Extent: {}'.format(
                n.get_data_spatial_extent()))
            data_range = n.get_data_range()
            click.echo(' Range of Values: min={} - max={}'.format(
                data_range[0], data_range[1]))
        except Exception as err:
            raise click.ClickException(str(err))


@click.command()
@click.pass_context
@click.option('--file', '-f', 'file_in',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to Numeric data file')
@click.option('--output', '-o', 'file_out',
              type=click.Path(exists=False, resolve_path=True),
              help='Path to output data file')
@click.option('--format', '-of', 'format_', help='Output format')
@click.option('--verbosity', type=click.Choice(['ERROR', 'WARNING',
              'INFO', 'DEBUG']), help='Verbosity')
def export(ctx, file_in, file_out, format_, verbosity):
    """parse Numeric data files"""

    if verbosity is not None:
        logging.basicConfig(level=getattr(logging, verbosity))
    else:
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    if file_in is None or file_out is None or format_ is None:
        raise click.ClickException('Missing arguments')

    with open(file_in) as fh:
        try:
            click.echo('Exporting {} to {} ({})'.format(file_in,
                       file_out, format_))
            n = Numeric(fh, filename=file_in)
            status = n.to_grid(filename=file_out, fmt=format_)
            if status:
                click.echo('Done')
        except Exception as err:
            raise click.ClickException(str(err))


cli.add_command(report)
cli.add_command(export)
