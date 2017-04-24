import argparse
from collections import ChainMap
from collections import OrderedDict
import dateutil.parser
import gdal
from gdalconst import GA_ReadOnly
import glob
import os
import platform
import pprint
import time
import uuid
import yaml

pp = pprint.PrettyPrinter(indent=4)

'''
This script accepts a path to your ASTER GDEM2 directory as its only argument. Make sure it ends with '/'

The meta data file we generate requires to following fields.

= EXTENT
= PRODUCT_TYPE
= PLATFORM
= INSTRUMENT
= FORMAT
= CREATION DATE
= UUID
= LINEAGE
= IMAGE BANDS
= PROJECTION INFO

As long as you point to an ASTER DEM V2 directory( looks like '/ASTGTM2_N05W076/', contains a
*_dem.tif file and *_num.tif file), all of these values will be generated. You should not have to worry about
changing any values in this preparation script. The spatial projection data is extracted from your _dem.tif courtesy of GDAL.

If you want to find hardcoded values in this script, ctrl + f 'hard_coded'
If you want to find values generated on the fly, ctrl + f 'on_the_fly_generated'
'''

def fetch_path_from_process_arguments():
	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description='This script is used to generate meta-data files for ASTER GDEM Version 2 . Be sure you include a _dem.tif file and _num.tif file.')
	parser.add_argument('-p','--path', help='A required parameter that points to your ASTER GDEM V2 directory. An ASTER GDEM directory looks like ../ASTGTM2_N05W076/. It should contain two TIFF files. One that ends with _dem.tif, another that ends with _num.tif', required=True)
	args = vars(parser.parse_args())
	path = args["path"]
	if path[-1] is not "/":
		path = path +"/"
	return path

def get_dem_path(partial):
	return glob.glob(partial + "ASTGTM2_N??W???_dem.tif")[0]

def get_num_path(partial):
	return glob.glob(partial + "ASTGTM2_N??W???_num.tif")[0]

def get_creation_dt(partial):
	dem = get_dem_path(partial)
	tiff_time = gdal.Open(dem).GetMetadata()["TIFFTAG_DATETIME"]
	creation_datetime = dateutil.parser.parse(tiff_time).strftime("%Y-%m-%d %T")
	return {"creation_dt": creation_datetime}

def get_extent(partial):
	dem_path = get_dem_path(partial)
	data = gdal.Open(dem_path, GA_ReadOnly)
	geoTransform = data.GetGeoTransform()
	minx = geoTransform[0]
	maxy = geoTransform[3]
	maxx = minx + geoTransform[1] * data.RasterXSize
	miny = maxy + geoTransform[5] * data.RasterYSize
	dem = get_dem_path(partial)
	tiff_time = gdal.Open(dem).GetMetadata()["TIFFTAG_DATETIME"]
	creation_datetime = dateutil.parser.parse(tiff_time).strftime("%Y-%m-%d %T")
	extent = {"extent": {"coord": {"ll": {"lat": miny, "lon": minx}, "lr": {"lat": miny, "lon": maxx}, "ul": {"lat": maxy, "lon": minx}, "ur": {"lat": maxy, "lon": maxx}},
	"center_dt": creation_datetime,
	}}
	return extent

def get_spatial_refference(partial):
	dem_path = get_dem_path(partial)
	data = gdal.Open(dem_path, GA_ReadOnly)
	geoTransform = data.GetGeoTransform()
	minx = geoTransform[0]
	maxy = geoTransform[3]
	maxx = minx + geoTransform[1] * data.RasterXSize
	miny = maxy + geoTransform[5] * data.RasterYSize
	geo_ref_points = {"geo_ref_points": {"ll": {"y": miny, "x": minx}, "lr": {"y": miny, "x": maxx}, "ul": {"y": maxy, "x": minx}, "ur": {"y": maxy, "x": maxx}}}
	projection_ref = { "spatial_reference": data.GetProjectionRef()}
	grid_spatial = {"grid_spatial": {"projection": dict(ChainMap({}, geo_ref_points, projection_ref))}}
	return grid_spatial

def get_image_bands(partial):
	dem_local_path = glob.glob(partial + "ASTGTM2_N??W???_dem.tif")[0].split('/')[-1]
	num_local_path = glob.glob(partial + "ASTGTM2_N??W???_num.tif")[0].split('/')[-1]
	aster_gdem_image_bands = {"image": {"bands":{"dem": {"path": dem_local_path}, "num": {"path": num_local_path} }}}
	return aster_gdem_image_bands

def get_lineage(partial):
	hard_coded_empty_lineage = {"lineage": {"source_datasets":{}}}
	return hard_coded_empty_lineage

def get_product_type(partial):
	hard_coded_product_type = {"product_type":"GDEM_V2"}
	return hard_coded_product_type

def get_dataset_id(partial):
	on_the_fly_generated_id = {"id": str(uuid.uuid4())}
	return on_the_fly_generated_id

def get_platform(partial):
	hard_coded_platform_name = {"platform": {"code": "TERRA"}}
	return hard_coded_platform_name

def get_instrument(partial):
	hard_coded_instrument_name = {"instrument": {"name": "ASTER"}}
	return hard_coded_instrument_name

def get_format(partial):
	hard_coded_file_format = {"format": {"name": "GeoTiff"}}
	return hard_coded_file_format

def write_dict_to_yaml(the_dict):
	output = yaml.dump(the_dict, default_flow_style=False, explicit_start=True)
	print(output)
def write_list_of_dicts_to_yaml(partial, dict_list):
	output = ""
	for item  in dict_list:
		output = output + yaml.dump(item, default_flow_style=False, explicit_start=False) + '\n'
	yaml_file_stream = open(partial + "aster_gdem2_metadata.yaml", "w")
	yaml_file_stream.write(output)
	yaml_file_stream.close()

################################################
#		CODE STARTS HERE
################################################

partial 	= fetch_path_from_process_arguments() #partial path
creation_dt 	= get_creation_dt(partial)
extent 		= get_extent(partial)
file_format  	= get_format(partial)
image_bands  	= get_image_bands(partial)
instrument 	= get_instrument(partial)
lineage 	= get_lineage(partial)
product_type 	= get_product_type(partial)
platform 	= get_platform(partial)
spatial_ref	= get_spatial_refference(partial)
uuid 		= get_dataset_id(partial)

configuration_list = [uuid, creation_dt, product_type, platform, instrument,
file_format, extent, spatial_ref, image_bands, lineage]

write_list_of_dicts_to_yaml(partial, configuration_list)
