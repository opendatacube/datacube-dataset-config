# coding=utf-8
"""
Ingest data from the command-line.
"""
from __future__ import absolute_import

import logging
import os
import uuid
from pathlib import Path
from xml.etree import ElementTree

import click
import rasterio.features
import shapely.affinity
import shapely.geometry
import shapely.ops
import yaml
from osgeo import osr
from rasterio.errors import RasterioIOError


# image boundary imports


# IMAGE BOUNDARY CODE

def safe_valid_region(images, mask_value=None):
    try:
        return valid_region(images, mask_value)
    except (OSError, RasterioIOError):
        return None


def valid_region(images, mask_value=None):
    mask = None
    for fname in images:
        # ensure formats match
        with rasterio.open(str(fname), 'r') as ds:
            transform = ds.affine

            img = ds.read(1)

            if mask_value is not None:
                new_mask = img & mask_value == mask_value
            else:
                # TODO update when sen2cor format write finalised new_mask = img != ds.nodata
                new_mask = img != 0
            if mask is None:
                mask = new_mask
            else:
                mask |= new_mask

    shapes = rasterio.features.shapes(mask.astype('uint8'), mask=mask)
    shape = shapely.ops.unary_union([shapely.geometry.shape(shape) for shape, val in shapes if val == 1])
    type(shapes)

    geom = shape.convex_hull

    # buffer by 1 pixel
    geom = geom.buffer(1, join_style=3, cap_style=3)

    # simplify with 1 pixel radius
    geom = geom.simplify(1)

    # intersect with image bounding box
    geom = geom.intersection(shapely.geometry.box(0, 0, mask.shape[1], mask.shape[0]))

    # transform from pixel space into CRS space
    geom = shapely.affinity.affine_transform(geom, (transform.a, transform.b, transform.d,
                                                    transform.e, transform.xoff, transform.yoff))

    output = shapely.geometry.mapping(geom)

    return geom


def _to_lists(x):
    """
    Returns lists of lists when given tuples of tuples
    """
    if isinstance(x, tuple):
        return [_to_lists(el) for el in x]

    return x


def get_geo_ref_points(root):
    nrows = int(root.findall('./*/Tile_Geocoding/Size[@resolution="10"]/NROWS')[0].text)
    ncols = int(root.findall('./*/Tile_Geocoding/Size[@resolution="10"]/NCOLS')[0].text)

    ulx = int(root.findall('./*/Tile_Geocoding/Geoposition[@resolution="10"]/ULX')[0].text)
    uly = int(root.findall('./*/Tile_Geocoding/Geoposition[@resolution="10"]/ULY')[0].text)

    xdim = int(root.findall('./*/Tile_Geocoding/Geoposition[@resolution="10"]/XDIM')[0].text)
    ydim = int(root.findall('./*/Tile_Geocoding/Geoposition[@resolution="10"]/YDIM')[0].text)

    return {
        'ul': {'x': ulx, 'y': uly},
        'ur': {'x': ulx + ncols * abs(xdim), 'y': uly},
        'll': {'x': ulx, 'y': uly - nrows * abs(ydim)},
        'lr': {'x': ulx + ncols * abs(xdim), 'y': uly - nrows * abs(ydim)},
    }


def get_coords(geo_ref_points, spatial_ref):
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lon, lat, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def prepare_dataset(path):
    root = ElementTree.parse(str(path)).getroot()
    level = root.findall('./*/Product_Info/PROCESSING_LEVEL')[0].text
    product_type = root.findall('./*/Product_Info/PRODUCT_TYPE')[0].text
    ct_time = root.findall('./*/Product_Info/GENERATION_TIME')[0].text
    print(level, product_type, ct_time)
    # granuleslist = [(granule.get('granuleIdentifier'), [imid.text for imid in granule.findall('IMAGE_FILE')]) for
    #                granule in
    #                root.findall('./*/Product_Info/Product_Organisation/Granule_List/Granules')]
    # Assume multiple granules
    single_granule_archive = False
    granules = {granule.get('granuleIdentifier'): [imid.text for imid in granule.findall('IMAGE_ID')]
                for granule in root.findall('./*/Product_Info/Product_Organisation/Granule_List/Granules')}
    if not granules:
        single_granule_archive = True
        granules = {granule.get('granuleIdentifier'): [imid.text for imid in granule.findall('IMAGE_FILE')]
                    for granule in root.findall('./*/Product_Info/Product_Organisation/Granule_List/Granule')}
        if not [] in granules.values():
            single_granule_archive = True
        else:
            granules = {granule.get('granuleIdentifier'): [imid.text for imid in granule.findall('IMAGE_ID')]
                        for granule in root.findall('./*/Product_Info/Product_Organisation/Granule_List/Granule')}
            single_granule_archive = False

    # current = 0
    # list = []
    # granules = {}
    # for i in granuleslist:
    #    granules[i[0]] = {}
    # for key in granules.keys():

    #    granulecontent = []
    #    for j in granuleslist:

    #        if key in j:
    #            granulecontent = granulecontent + j[1]

    #    granules[key] = granulecontent
    grouped_images = []
    documents = []
    for granule_id, images in granules.items():
        images_ten_list = []
        images_twenty_list = []
        images_sixty_list = []
        images_classification = []
        # gran_path = str(path.parent.joinpath('GRANULE', granule_id, granule_id[:-7].replace('MSI', 'MTD') + '.xml'))
        img_data_path = str(path.parent.joinpath('GRANULE', granule_id, 'IMG_DATA'))

        gran_path = str(path.parent.joinpath('GRANULE', granule_id, granule_id[:-7].replace('MSI', 'MTD') + '.xml'))
        if not Path(gran_path).exists():
            gran_path = str(path.parent.joinpath(images[0]))
            gran_path = str(Path(gran_path).parents[2].joinpath('MTD_TL.xml'))
        root = ElementTree.parse(gran_path).getroot()

        if not Path(img_data_path).exists():
            # img_data_path = str(Path(gran_path).parents[0].joinpath('IMG_DATA'))
            img_data_path = str(Path(path).parent)

        if single_granule_archive is False:
            img_data_path = img_data_path + str(Path('GRANULE').joinpath(granule_id, 'IMG_DATA'))

        root = ElementTree.parse(gran_path).getroot()
        sensing_time = root.findall('./*/SENSING_TIME')[0].text
        # img_data_path = str(path.parent.joinpath('GRANULE', granule_id, 'IMG_DATA'))
        # img_data_path_r10 = str(Path(img_data_path).joinpath('R10m'))
        # img_data_path_r20 = str(path.parent.joinpath('GRANULE', granule_id, 'IMG_DATA', 'R20m'))
        # img_data_path_r60 = str(path.parent.joinpath('GRANULE', granule_id, 'IMG_DATA', 'R60m'))

        for image in images:
            # print('IMAGE',image)
            # print('img_data_path', img_data_path)
            # image = str(Path(image).name)
            # print('IMAGE',image)
            classification_list = ['SCL']
            ten_list = ['B02_10m', 'B03_10m', 'B04_10m', 'B08_10m']
            twenty_list = ['B05_20m', 'B06_20m', 'B07_20m', 'B11_20m', 'B12_20m', 'B8A_20m',
                           'B02_20m', 'B03_20m', 'B04_20m']
            sixty_list = ['B01_60m', 'B02_60m', 'B03_60m', 'B04_60m', 'B8A_60m', 'B09_60m',
                          'B05_60m', 'B06_60m', 'B07_60m', 'B11_60m', 'B12_60m']

            for item in classification_list:
                if item in image:
                    # TODO include 60m classification
                    if '20m' in image:
                        images_classification.append(os.path.join(str(path.parent), image + ".jp2"))

            for item in ten_list:
                if item in image:
                    images_ten_list.append(os.path.join(str(path.parent), image + ".jp2"))
                    grouped_images.append(os.path.join(str(path.parent), image + ".jp2"))
            for item in twenty_list:
                if item in image:
                    images_twenty_list.append(os.path.join(str(path.parent), image + ".jp2"))
                    grouped_images.append(os.path.join(str(path.parent), image + ".jp2"))
            for item in sixty_list:
                if item in image:
                    images_sixty_list.append(os.path.join(str(path.parent), image + ".jp2"))
                    grouped_images.append(os.path.join(str(path.parent), image + ".jp2"))

        station = root.findall('./*/Archiving_Info/ARCHIVING_CENTRE')[0].text

        cs_code = root.findall('./*/Tile_Geocoding/HORIZONTAL_CS_CODE')[0].text
        spatial_ref = osr.SpatialReference()

        spatial_ref.SetFromUserInput(cs_code)

        spectral_dict = {image[-11:-4]: {'path': str(Path(image)), 'layer': 1, } for image in grouped_images}
        scl_dict = {'SCL_20m': {'path': str(Path(classification)), 'layer': 1, } for classification in
                    images_classification}
        spectral_dict.update(scl_dict)

        geo_ref_points = get_geo_ref_points(root)

        documents.append({
            'id': str(uuid.uuid4()),
            'processing_level': level.replace('Level-', 'L'),
            'product_type': product_type,
            'creation_dt': ct_time,
            'platform': {'code': 'SENTINEL_2A'},
            'instrument': {'name': 'MSI'},
            'acquisition': {'groundstation': {'code': station}},
            'extent': {
                'from_dt': sensing_time,
                'to_dt': sensing_time,
                'center_dt': sensing_time,
                'coord': get_coords(geo_ref_points, spatial_ref),
            },
            'format': {'name': 'JPEG2000'},
            'grid_spatial': {
                'projection': {
                    'geo_ref_points': geo_ref_points,
                    'spatial_reference': spatial_ref.ExportToWkt(),
                    # TODO revisit sen2cor jp2 file info incomplete - skip valid_data for now
                    # 'valid_data': {
                    #    'coordinates': _to_lists(
                    #        shapely.geometry.mapping(
                    #            shapely.ops.unary_union([
                    #                safe_valid_region(images_sixty_list)
                    #            ])
                    #        )['coordinates']),
                    #    'type': "Polygon"}
                }
            },
            'image': {
                'bands': spectral_dict
            },

            'lineage': {'source_datasets': {}},
        })
    return documents


@click.command(
    help="Prepare Sentinel 2 L2 sen2cor dataset SR and SC for ingestion into the Data Cube. "
         "eg. python sen2cor_prepare.py <input>.SAFE --output <outfile>.yaml")
@click.argument('datasets',
                type=click.Path(exists=True, readable=True, writable=False),
                nargs=-1)
@click.option('--output', help="Write datasets into this directory",
              type=click.Path(exists=False, writable=True, dir_okay=True))
def main(datasets, output):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    for dataset in datasets:

        path = Path(dataset).absolute()
        if path.is_dir():
            # path = Path(path.joinpath(path.stem.replace('PRD_MSIL2A', 'MTD_SAFL2A') + '.xml'))
            for file in os.listdir(path):
                if file.endswith(".xml"):
                    if file.startswith("MTD"):
                        path = Path(os.path.join(path, file))
        if path.suffix != '.xml':
            raise RuntimeError('want xml')

        logging.info("Processing %s", path)

        documents = prepare_dataset(path)

        output_path = Path(output)
        if 'xml' in str(path):
            yaml_path = output_path.joinpath(path.parent.name + '.yaml')
        else:
            yaml_path = output_path.joinpath(path.name + '.yaml')

        if documents:
            logging.info("Writing %s dataset(s) into %s", len(documents), yaml_path)
            with open(yaml_path, 'w') as stream:
                yaml.dump_all(documents, stream)
        else:
            logging.info("No datasets discovered. Bye!")


if __name__ == "__main__":
    main()
