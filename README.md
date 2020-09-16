# odc-dataset-config
Scripts for indexing data into ODC instances

# GDAL3
Please note - we are aware that using these scripts with GDAL 3.0+ can cause Latitudes and Longitudes to become transposed. When using these scripts, please use a python environment with an earlier version of GDAL.


# odc-product-delete (In beta)
SQL scripts to delete ODC products and related records in ODC, Explorer and OWS DB. Each script takes product_name as an input parameter.

Usage:
```
psql -v product_name=<product-to-delete> -f <scriptname.sql> -h <database-hostname> <dbname>
```

- `delete_odc_product.sql` 
    - This script will delete ODC product from ODC DB. 
    - It deletes records from tables `agdc.dataset_source`, `agdc.dataset_location`, `agdc.dataset` and `agdc.dataset_type`.
    - It also deletes indexes and view related to the ODC product.
    
- `delete_odc_product_explorer.sql` 
    - This script will delete records related to ODC product from Explorer DB. 
    - It deletes records from these tables `cubedash.dataset_spatial`, `cubedash.time_overview`, `cubedash.product`.
    - Also, it refreshes materialised view `cubedash.mv_dataset_spatial_quality`.

- `delete_odc_product_ows.sql`
    - This script will delete records from tables `wms.product_ranges` and `wms.sub_product_ranges`. 
    - This script needs to be run before `delete_odc_product.sql` as OWS DB maintains a foreign key to ODC DB.
    - Table `agdc.dataset_type` has foreign key constraint `wms.product_ranges_id_fkey` on table `wms.product_ranges`

Notes: 
- AS ODC doesn't have product deletion feature with an intention to keep an immutable history of datasets, these scripts are created to manually delete an entire ODC Product. 
- To be noted this scripts are still in beta testing phase.