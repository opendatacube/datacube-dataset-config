# Delete ODC Product (In beta)

- AS ODC doesn't have product deletion feature with an intention to keep an immutable history of datasets, following scripts are created to manually delete an entire ODC Product and related records in ODC, Explorer and OWS DB.
    - `delete_odc_product_ows.sql`
    - `delete_odc_product.sql`
    - `delete_odc_product_explorer.sql`

## WARNING!!!
- These scripts deletes data, so review the scripts thoroughly and use it very carefully!

### Usage
- Use with PSQL from the command line. Each script takes <product_name> and DB credentials as an input parameter.

```
psql -v product_name=<product-to-delete> -f <scriptname.sql> -h <database-hostname> <dbname>
```

## Delete ODC Product from OWS (`delete_odc_product_ows.sql`)

- Before deleting product from ODC DB, we need check if the product has been added to OWS.
- If the product has been added to OWS, some of these tables have a foreign key constraint with ODC table, which will prevent rows being deleted from the main ODC database.
- Table `agdc.dataset_type` has foreign key constraint `wms.product_ranges_id_fkey` on table `wms.product_ranges`
- Because of the foreign key constraint, deleting datasets for a product in the ODC DB will fail and raise following error:
```
- ERROR:  update or DELETE on table "dataset_type" violates foreign key constraint "product_ranges_id_fkey" on table "product_ranges"
- DETAIL:  Key (id)=(1) is still referenced from table "product_ranges".
```
- To avoid this, there is a need to run `delete_odc_product_ows.sql` script before running `delete_odc_product.sql`.
- This script will delete records from tables `wms.product_ranges` and `wms.sub_product_ranges`.

## Delete ODC Product from Explorer (`delete_odc_product_explorer.sql` )

- Before deletion of an product in ODC DB, Explorer's Schema needs to be cleaned as this script makes reference to ODC DB.
- This script will delete records related to an ODC product from the Explorer Schema in the ODC DB.
- It unnests the product id `derived_product_refs` and `source_product_refs` columns from `cubedash.product` table
- It deletes records from these tables `cubedash.region`, `cubedash.dataset_spatial`, `cubedash.time_overview`, `cubedash.product`.
- Also, it refreshes materialised view `cubedash.mv_dataset_spatial_quality`.


## Delete ODC Product from ODC DB (`delete_odc_product.sql`)

- This script will delete a product and all datasets from an ODC DB.
- It will delete lineage records from the table `agdc.dataset_source`.
- It will delete location records from the table `agdc.dataset_location`.
- It deletes dataset records from the table `agdc.dataset`.
- It deletes the product from the table `agdc.dataset_type`.
- It also deletes indexes and view created for that ODC product.

Note: The `delete_odc_product.sql` is sourced from [here](https://gist.github.com/omad/1ae3463a123f37a9acf37213bebfde86) and additional script to delete index and view are added.


## Steps to run scripts in sequence
- First, run `delete_odc_product_ows.sql` (optional: this step is not required if the product has not been added to OWS).
```
psql -v product_name=<product-to-delete> -f delete_odc_product_ows.sql -h <database-hostname> <dbname>
```
- Next run `delete_odc_product_explorer.sql` to delete products from Explorer DB.
```
psql -v product_name=<product-to-delete> -f delete_odc_product_explorer.sql -h <database-hostname> <dbname>
```
- Finally run `delete_odc_product.sql` to delete the ODC product in ODC DB.
```
psql -v product_name=<product-to-delete> -f delete_odc_product.sql -h <database-hostname> <dbname>
```

## Detailed Steps to run scripts in sequence
- setup env
```
export DB_PORT=5432
export DB_DATABASE=dbname
export DB_HOSTNAME=localhost
```
- First, run `delete_odc_product_ows.sql` (optional: this step is not required if the product has not been added to OWS).
```
export DB_USERNAME=ows_admin
export DB_PASSWORD=<ows_admin_password>
PGPASSWORD=$DB_PASSWORD psql -v product_name=<product-to-delete> -f delete_odc_product_ows.sql -h $DB_HOSTNAME $DB_DATABASE -U $DB_USERNAME -p $DB_PORT
```
- Next run `delete_odc_product_explorer.sql` to delete products from Explorer DB.
```
export DB_USERNAME=explorer_admin
export DB_PASSWORD=<explorer_admin_password>
PGPASSWORD=$DB_PASSWORD psql -v product_name=<product-to-delete> -f delete_odc_product_explorer.sql -h $DB_HOSTNAME $DB_DATABASE -U $DB_USERNAME -p $DB_PORT
```
- Finally run `delete_odc_product.sql` to delete the ODC product in ODC DB.
```
export DB_USERNAME=odc_admin
export DB_PASSWORD=<odc_admin_password>
PGPASSWORD=$DB_PASSWORD psql -v product_name=<product-to-delete> -f delete_odc_product.sql -h $DB_HOSTNAME $DB_DATABASE -U $DB_USERNAME -p $DB_PORT
```