# coding=utf-8
"""
Ingest data from the command-line.
"""
from __future__ import absolute_import, division

import logging
import uuid
from xml.etree import ElementTree
import re
from pathlib import Path
import yaml
from dateutil import parser
from datetime import timedelta
import rasterio.warp
import click
from osgeo import osr
import os
import gdal
import sys
from osgeo import gdal, ogr, osr
from datetime import datetime


def GetExtent(gt, cols, rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext = []
    xarr = [0, cols]
    yarr = [0, rows]

    for px in xarr:
        for py in yarr:
            x = gt[0] + (px * gt[1]) + (py * gt[2])
            y = gt[3] + (px * gt[4]) + (py * gt[5])
            ext.append([x, y])
        yarr.reverse()
    return ext


def ReprojectCoords(coords, src_srs, tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords = []
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    for x, y in coords:
        x, y, z = transform.TransformPoint(x, y)
        trans_coords.append([x, y])
    return trans_coords


def getExtents(nbar_path, prep_file):
    ds = gdal.Open(str(nbar_path) + "/" + prep_file)
    gt = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ext = GetExtent(gt, cols, rows)

    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(ds.GetProjection())
    tgt_srs = src_srs.CloneGeogCS()

    geo_ext = ReprojectCoords(ext, src_srs, tgt_srs)
    return geo_ext


def processBandParams(bands):
    band_list = {}
    for band in bands:
        band_array = band.split("=")
        band_list[str(band_array[0])] = str(band_array[1])

    return band_list


def prep_dataset(nbar_path, prep_file, processing_level, product_type, platform_code, instrument, bands):
    extents = getExtents(nbar_path, prep_file)
    coord_upper_left = extents[0]
    coord_upper_right = extents[3]
    coord_lower_left = extents[1]
    coord_lower_right = extents[2]

    with rasterio.open(str(nbar_path) + "/" + prep_file) as src:
        left = src.bounds.left
        right = src.bounds.right
        top = src.bounds.top
        bottom = src.bounds.bottom

    band_dict = processBandParams(bands)
    src_ds = gdal.Open(str(nbar_path) + "/" + prep_file)
    images = {}
    for band in range(src_ds.RasterCount):
        band += 1
        srcband = src_ds.GetRasterBand(band)
        images[str(band_dict[str(band)])] = {'path': prep_file, 'layer': srcband.GetBand()}

    doc = {
        'id': str(uuid.uuid4()),
        'processing_level': str(processing_level),
        'product_type': str(product_type),
        'creation_dt': datetime.strptime(prep_file.split("_")[3] + '-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
        'platform': {
            'code': str(platform_code)
        },
        'instrument': {
            'name': str(instrument)
        },
        'extent': {
            'from_dt': datetime.strptime(prep_file.split("_")[3] + '-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
            'to_dt': datetime.strptime(prep_file.split("_")[3] + '-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
            'center_dt': datetime.strptime(prep_file.split("_")[3] + '-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
            'coord': {
                'll': {
                    'lat': coord_lower_left[1],
                    'lon': coord_lower_left[0]
                },
                'lr': {
                    'lat': coord_lower_right[1],
                    'lon': coord_lower_right[0]
                },
                'ul': {
                    'lat': coord_upper_left[1],
                    'lon': coord_upper_left[0]
                },
                'ur': {
                    'lat': coord_upper_right[1],
                    'lon': coord_upper_right[0]
                },
            }
        },
        'format': {
            'name': 'GeoTiff'
        },
        'grid_spatial': {
            'projection': {
                'spatial_reference': str(src.crs.wkt),
                'geo_ref_points': {
                    'ul': {
                        'x': left,
                        'y': top
                    },
                    'ur': {
                        'x': right,
                        'y': top
                    },
                    'll': {
                        'x': left,
                        'y': bottom
                    },
                    'lr': {
                        'x': right,
                        'y': bottom
                    },
                }
            }
        },
        'image': {
            'satellite_ref_point_start': {
                'x': prep_file.split("_")[1],
                'y': prep_file.split("_")[2]
            },
            'satellite_ref_point_end': {
                'x': prep_file.split("_")[1],
                'y': prep_file.split("_")[2]
            },
            'bands': images
        },
        'lineage': {
            'source_datasets': {}
        }
    }

    if instrument is None:
        doc.pop("instrument", None)  # Pop the key if there is no entry
    return doc


@click.command(
    help="Prepare Layered GeoTIFF ingestion into the Data Cube. Example command: python single_layer_tif_prepare.py /datacube/original_data/Colombia/ -l sr_refl -t LEDAPS -c LANDSAT_7 -i ETM -b 1=sr_band3 -b 2=sr_band4 -b 3=sr_band5 -b 4=sr_band7"
)
@click.argument('datasets', type=click.Path(exists=True, readable=True, writable=True), nargs=-1)
@click.option('-l', '--processing_level', help='Set the processing level (ex. sr_refl).')
@click.option('-t', '--product-type', help='Set the product type (ex. LEDAPS).')
@click.option('-c', '--platform_code', help='Set the platform code (ex. LANDSAT_7).')
@click.option('-i', '--instrument', help='Set the instrument.')
@click.option(
    '-b',
    '--bands',
    multiple=True,
    help='Pass in a band number and the associated name (ex. -b 1=swir -b 2=red -b 3=blue ...)')
def main(datasets, processing_level, product_type, platform_code, instrument, bands):
    arg_product_type = ''
    arg_platform_code = ''
    arg_instrument = ''

    arg_processing_level = str(processing_level) if processing_level is not None else 'sr_refl'
    arg_product_type = str(product_type) if product_type is not None else 'LEDAPS_MOSAIC'
    arg_platform_code = str(platform_code) if platform_code is not None else 'LANDSAT_7'
    arg_instrument = str(instrument) if instrument is not None else 'ETM'

    arg_bands = bands if len(bands) > 0 else ["1=sr_band3", "2=sr_band4", "3=sr_band5", "4=sr_band7"]

    if arg_product_type is None or arg_platform_code is None:
        print(
            "Product Type and Platform Code must be included to run the script. Please include these parameters and run the script again."
        )
        sys.exit(2)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    print("Entering program")
    for dataset in datasets:
        path = Path(dataset)
        logging.info("Processing %s", path)

        for file in os.listdir(str(path)):
            if file.endswith(".img") or file.endswith(".tif"):
                print("Found file...")
                print("Preparing file: " + str(path) + "/" + file)
                data = prep_dataset(path, file, arg_processing_level, arg_product_type, arg_platform_code,
                                    arg_instrument, arg_bands)
                file_name = file.split(".")[0]
                yaml_path = str(path.joinpath(file_name + '.yaml'))
                logging.info("Writing %s", yaml_path)
                with open(yaml_path, 'w') as stream:
                    yaml.dump(data, stream)


if __name__ == "__main__":
    main()
