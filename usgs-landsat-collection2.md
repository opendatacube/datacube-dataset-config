# Indexing USGS' Landsat Collection 2

Landsat data is available from a public bucket located in the Oregon region of AWS. The
bucket is `s3://usgs-landsat` and requires "requester pays" access.

``` bash
aws s3 ls --request-payer requester s3://usgs-landsat/collection02/level-2/
```

An [ODC product definition for the Landsat surface reflectance data](products/lsX_c2l2_sr.odc-product.yaml) is inluded in this repo. Add this to datacube using the following command:

``` bash
datacube product add products/lsX_c2l2_sr.odc-product.yaml
```

or

``` bash
datacube product add https://raw.githubusercontent.com/opendatacube/datacube-dataset-config/main/products/lsX_c2l2_sr.odc-product.yaml
```

## Installing the required tools

Install the scripts required by [following the instructions here](https://github.com/opendatacube/odc-tools/tree/develop/apps/dc_tools) like this:

```bash
pip install odc_apps_dc_tools
```

Note that because of the requester pays requirement, you must have AWS credentials present in the environment you're working in.

## Indexing from a STAC API

Indexing for a region of interest can be done using the STAC API, like this:

```bash
stac-to-dc \
--catalog-href='https://landsatlook.usgs.gov/stac-server/' \
--rewrite-assets='https://landsatlook.usgs.gov/data/,s3://usgs-landsat/' \
--bbox='25,20,35,30' \
--collections='landsat-c2l2-sr' \
--datetime='2020-01-01/2020-03-31'
```

> Added 707 Datasets, failed 0 Datasets

You can change the bounding box or datetime range to search anywhere in the world.

## Note about requester pays

Please note that you must use AWS credentials to access the data from the requester pays bucket.
The USGS has information about [cloud data access here](https://www.usgs.gov/node/28686).

There are [some docs here](https://datacube-core.readthedocs.io/en/latest/api/utilities/generate/datacube.utils.aws.configure_s3_access.html?highlight=requester_pays) on how to set up the requester pays flag using the ODC.
