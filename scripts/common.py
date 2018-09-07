import logging

import rasterio
import rasterio.features
import shapely.affinity
import shapely.geometry
import shapely.ops
from datacube.index.hl import Doc2Dataset
from datacube.utils import changes
from rasterio import RasterioIOError


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
            transform = ds.transform
            img = ds.read(1)

            if mask_value is not None:
                new_mask = img & mask_value == mask_value
            else:
                new_mask = img != ds.nodata
            if mask is None:
                mask = new_mask
            else:
                mask |= new_mask

    shapes = rasterio.features.shapes(mask.astype('uint8'), mask=mask)
    shape = shapely.ops.unary_union([shapely.geometry.shape(shape) for shape, val in shapes if val == 1])

    # convex hull
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
    output['coordinates'] = _to_lists(output['coordinates'])
    return output


def _to_lists(x):
    """
    Returns lists of lists when given tuples of tuples
    """
    if isinstance(x, tuple):
        return [_to_lists(el) for el in x]

    return x


def get_grid_spatial_projection(fname):
    with rasterio.open(fname, 'r') as img:
        left, bottom, right, top = img.bounds
        spatial_reference = str(str(getattr(img, 'crs_wkt', None) or img.crs.wkt))
        geo_ref_points = {
            'ul': {'x': left, 'y': top},
            'ur': {'x': right, 'y': top},
            'll': {'x': left, 'y': bottom},
            'lr': {'x': right, 'y': bottom},
        }
        return geo_ref_points, spatial_reference


def archive_dataset(doc, uri, index, sources_policy):
    def get_ids(dataset):
        ds = index.datasets.get(dataset.id, include_sources=True)
        for source in ds.sources.values():
            yield source.id
        yield dataset.id

    resolver = Doc2Dataset(index)
    dataset, err = resolver(doc, uri)
    index.datasets.archive(get_ids(dataset))
    logging.info("Archiving %s and all sources of %s", dataset.id, dataset.id)


def add_dataset(doc, uri, index, sources_policy):
    logging.info("Indexing %s", uri)
    resolver = Doc2Dataset(index)
    dataset, err = resolver(doc, uri)
    if err is not None:
        logging.error("%s", err)
    try:
        index.datasets.add(dataset,
                           sources_policy=sources_policy)  # Source policy to be checked in sentinel 2 datase types
    except changes.DocumentMismatchError as e:
        index.datasets.update(dataset, {tuple(): changes.allow_any})
    except Exception as e:
        logging.error("Unhandled exception %s", e)

    return uri
