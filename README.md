# Datacube Dataset Config Examples and Scripts

Scripts for indexing data into ODC instances.

## Documented Examples

* [Sentinel-2 Cloud-Optimised GeoTIFFs.][sentinel-2-l2a-cogs.md]

## GDAL3 Note

Please note - we are aware that using these scripts with GDAL 3.0+ can cause Latitudes and Longitudes to become transposed. When using these scripts, please use a python environment with an earlier version of GDAL.

## odc-product-delete (In beta)

SQL scripts to delete ODC products and related records in ODC, Explorer and OWS DB. Each script takes product_name as an input parameter.

Usage:

``` bash
psql -v product_name=<product-to-delete> -f <scriptname.sql> -h <database-hostname> <dbname>
```

* `delete_odc_product.sql`
  * This script will delete a product and all datasets from an ODC DB. 
  * It deletes records from tables `agdc.dataset_source`, `agdc.dataset_location`, `agdc.dataset` and `agdc.dataset_type`.
  * It also deletes indexes and view related to the ODC product.

* `delete_odc_product_explorer.sql`
  * This script will delete records related to an ODC product from the Explorer Schema in the ODC DB.
  * This script needs to be run before `delete_odc_product.sql` as script makes reference to ODC DB.
  * It deletes records from these tables `cubedash.dataset_spatial`, `cubedash.time_overview`, `cubedash.product`.
  * Also, it refreshes materialised view `cubedash.mv_dataset_spatial_quality`.

* `delete_odc_product_ows.sql`
  * This script will delete records from tables `wms.product_ranges` and `wms.sub_product_ranges`. 
  * This script needs to be run before `delete_odc_product.sql` as OWS DB maintains a foreign key to ODC DB.
  * Table `agdc.dataset_type` has foreign key constraint `wms.product_ranges_id_fkey` on table `wms.product_ranges`

### WARNING

* AS ODC doesn't have product deletion feature with an intention to keep an immutable history of datasets, these scripts are created to manually delete an entire ODC Product. 
* These scripts deletes data, so review the scripts thoroughly and use it very carefully!
* For more detail, read [here](./odc-product-delete//README.md)
