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
import datetime
import rasterio.warp
import click
from osgeo import osr
import os
# image boundary imports
import rasterio
from rasterio.errors import RasterioIOError
import rasterio.features
import shapely.affinity
import shapely.geometry
import shapely.ops


def band_name(path):
    str_path = str(path)
    if '.ice.tif' in str_path:
        return 'ice_precipitation'
    if '.liquid.tif' in str_path:
        return 'liquid_precipitation'
    if '.liquidPercent.tif' in str_path:
        return 'percent_liquid'
    return 'total_precipitation'


def get_product_type_from_code(code):
    product_type = {'DAY': 'daily', 'MO': 'monthly', 'HHR': 'hourly'}
    return product_type[code]


def get_projection(path):
    with rasterio.open(str(path)) as img:
        left, bottom, right, top = img.bounds
        return {
            'spatial_reference':
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]',
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


def get_coords(geo_ref_points, spatial_ref):
    spatial_ref = osr.SpatialReference(spatial_ref)
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lon, lat, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def populate_coord(doc):
    proj = doc['grid_spatial']['projection']
    doc['extent']['coord'] = get_coords(proj['geo_ref_points'], proj['spatial_reference'])


def prep_dataset(fields, path):
    images = {band_name(im_path): {'path': str(im_path.relative_to(path))} for im_path in path.glob('*.tif')}
    projdict = get_projection(path / next(iter(images.values()))['path'])
    doc = {
        'id': str(uuid.uuid4()),
        'processing_level': fields["processing_level"],
        'product_type': fields["product_type"],
        'creation_dt': fields["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
        'platform': {
            'code': "GPM"
        },
        'instrument': {
            'name': "GPM"
        },
        'extent': {
            'from_dt':
            fields["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            'to_dt':
            fields["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
            'center_dt':
            (fields["start_time"] + (fields["end_time"] - fields["start_time"]) / 2).strftime("%Y-%m-%d %H:%M:%S")
        },
        'format': {
            'name': 'GeoTiff'
        },
        'grid_spatial': {
            'projection': projdict
        },
        'image': {
            'bands': images
        },
        'lineage': {
            'source_datasets': {}
        }
    }
    populate_coord(doc)
    return doc


def prepare_datasets(gpm_path):
    underscore_replacement = Path(str(gpm_path).replace('.', '_'))
    fields = re.match(("3B-"
                       r"(?P<duration>HHR|DAY|MO)"
                       "-GIS_MS_MRG_3IMERG_"
                       r"(?P<product_year>[0-9]{4})"
                       r"(?P<product_month>[0-9]{2})"
                       r"(?P<product_day>[0-9]{2})"
                       "-S"
                       r"(?P<start_hour>[0-9]{2})"
                       r"(?P<start_minute>[0-9]{2})"
                       r"(?P<start_second>[0-9]{2})"
                       "-E"
                       r"(?P<end_hour>[0-9]{2})"
                       r"(?P<end_minute>[0-9]{2})"
                       r"(?P<end_second>[0-9]{2})"
                       "_"
                       r"(?P<sequence_indicator>(?<=_).*?(?=_))"
                       "_"
                       r"(?P<version>\w{4})"), underscore_replacement.stem).groupdict()
    fields.update({
        'processing_level':
        fields['version'],
        'product_type':
        get_product_type_from_code(fields['duration']),
        'start_time':
        datetime.datetime(
            int(fields['product_year']),
            int(fields['product_month']),
            int(fields['product_day']),
            int(fields['start_hour']), int(fields['start_minute']), int(fields['start_second'])),
        'end_time':
        datetime.datetime(
            int(fields['product_year']),
            int(fields['product_month']),
            int(fields['product_day']), int(fields['end_hour']), int(fields['end_minute']), int(fields['end_second']))
    })
    gpm = prep_dataset(fields, gpm_path)
    return (gpm, gpm_path)


@click.command(help="Prepare GPM IMERG GIS products for ingestion into the Data Cube.")
@click.argument('datasets', type=click.Path(exists=True, readable=True, writable=True), nargs=-1)
def main(datasets):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    for dataset in datasets:

        path = Path(dataset)

        logging.info("Processing %s", path)
        documents = prepare_datasets(path)

        dataset, folder = documents
        yaml_path = str(folder.joinpath('datacube-metadata.yaml'))
        logging.info("Writing %s", yaml_path)
        with open(yaml_path, 'w') as stream:
            yaml.dump(dataset, stream)


if __name__ == "__main__":
    main()
