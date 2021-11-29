# Indexing Sentinel-2 Cloud-Optimised GeoTIFFs

Sentinel-2 data is available from a public bucket located in Oregon, for more
information see the [AWS PDS page](https://registry.opendata.aws/sentinel-2-l2a-cogs/).

There are two ways to index this data that are briefly outlined below.

An [ODC product definition for the S-2 COGs](products/s2_l2a.odc-product.yaml) is inluded in this repo. Add this to datacube using the following command:

```bash
datacube product add products/s2_l2a.odc-product.yaml
```

## Installing the required tools

Install the scripts required by [following the instructions here](https://github.com/opendatacube/odc-tools/tree/develop/apps/dc_tools) like this:

```bash
pip install --extra-index-url="https://packages.dea.ga.gov.au" odc_apps_dc_tools
```

You should export the following environment variables:

```bash
# Tell GDAL to not sign requests for data from S3
AWS_NO_SIGN_REQUEST=true
```

## Indexing static STAC documents

A single STAC document can be indexed direct from S3 like this:

```bash
s3-to-dc --stac --no-sign-request \
s3://deafrica-sentinel-2/sentinel-s2-l2a-cogs/37/M/CS/2017/10/**/S2A_37MCS_20171016_0_L2A.json s2_l2a
```

Or all scenes for a single MGRS code like this:

```bash
s3-to-dc --stac --no-sign-request \
"s3://deafrica-sentinel-2/sentinel-s2-l2a-cogs/37/M/CS/**/*S2A_37MCS_20171016_0_L2A*.json" s2_l2a
```

If successful, you should see a message that reads something like this:

> Added 634 Datasets, Failed 0 Datasets

## Indexing from a STAC API

Indexing for a region of interest can be done using the STAC API, like this:

```bash
stac-to-dc \
--catalog-href='https://earth-search.aws.element84.com/v0/' \
--bbox='25,20,35,30' \
--collections='sentinel-s2-l2a-cogs' \
--datetime='2020-01-01/2020-03-31'
```

You can change the bounding box or datetime range to search anywhere in the world.
