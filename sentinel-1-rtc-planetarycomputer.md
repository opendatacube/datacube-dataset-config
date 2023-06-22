# Indexing Sentinel-1 RTC Data

[Sentinel-1 radiometrically terrain corrected](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc)
data is available from the Microsoft Planetary Computer (MPC).

This can be indexed and used in the ODC, though you do require a MPC
account and to sign URLs to access it. This process is documented below.

```bash
datacube product add products/s1_rtc.odc-product.yaml
```

## Installing the required tools

Install the scripts required by [following the instructions here](https://github.com/opendatacube/odc-tools/tree/develop/apps/dc_tools) like this:

```bash
pip install odc_apps_dc_tools planetary_computer
```

## Indexing from a STAC API

Indexing for a region of interest can be done using the STAC API, like this
example over Samoa:

```bash
stac-to-dc \
--catalog-href='https://planetarycomputer.microsoft.com/api/stac/v1/' \
--bbox='-180.0,-20.0,-170.0, -10.0' \
--collections='sentinel-1-rtc' \
--datetime='2023-01-01/2023-06-30'
```

This should result in something like:

> Indexing from STAC API...
> Added 184 Datasets, failed 0 Datasets, skipped 0 Datasets

You can change the bounding box or datetime range to search anywhere in the world.

## Testing that you can access data

``` python
import datacube
from planetary_computer import sign_url

dc = datacube.Datacube(app='s1-example')

datasets = dc.find_datasets(product="sentinel_1_rtc")
print(f"Found {len(datasets)} datasets")

# To load data, you must include the `patch_url` parameter and export the
# environment variable PC_SDK_SUBSCRIPTION_KEY. See MPC docs for more information.
data = dc.load(datasets=datasets[0:1], output_crs="EPSG:3832", resolution=(-100, 100), patch_url=sign_url)
data = data.where(data.vv != -32768)

data
```
