# Delete ODC Product (In beta)

- AS ODC doesn't have product deletion feature with an intention to keep an immutable history of datasets, following scripts are created to manually delete an entire ODC Product and related records in ODC, Explorer and OWS DB.
  - `delete_odc_product_ows.sql`
  - `delete_odc_product.sql`
  - `delete_odc_product_explorer.sql`
  - `cleanup_explorer.sql`
  - `cleanup_odc_indexes.sql`

## WARNING

- These scripts deletes data, so review the scripts thoroughly and use it very carefully!

### Usage

- Use with PSQL from the command line. Each script takes <product_name> and DB credentials as an input parameter.
- To run them with standard Datacube environment variables, it's suggested that you also export `PRODUCT_NAME`

A simple example is to do the following:

``` bash
psql -v product_name=<product-to-delete> -f <scriptname.sql> -h <database-hostname> <dbname>
```

A more streamlined way is to do the following:

``` bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f delete_odc_product.sql -v product_name=$PRODUCT_NAME
```

## Delete ODC Product from OWS (`delete_odc_product_ows.sql`)

- Before deleting product from ODC DB, we need check if the product has been added to OWS.
- If the product has been added to OWS, some of these tables have a foreign key constraint with ODC table, which will prevent rows being deleted from the main ODC database.
- Table `agdc.dataset_type` has foreign key constraint `wms.product_ranges_id_fkey` on table `wms.product_ranges`
- Because of the foreign key constraint, deleting datasets for a product in the ODC DB will fail and raise following error:

> ERROR:  update or DELETE on table "dataset_type" violates foreign key constraint "product_ranges_id_fkey" on table "product_ranges"
> DETAIL:  Key (id)=(1) is still referenced from table "product_ranges".

- To avoid this, there is a need to run `delete_odc_product_ows.sql` script before running `delete_odc_product.sql`.
- This script will delete records from tables `wms.product_ranges` and `wms.sub_product_ranges`.

## Delete ODC Product from Explorer (`delete_odc_product_explorer.sql` )

- Before deletion of an product in ODC DB, Explorer's Schema needs to be cleaned as this script makes reference to ODC DB.
- This script will delete records related to an ODC product from the Explorer Schema in the ODC DB.
- It unnests the product id `derived_product_refs` and `source_product_refs` columns from `cubedash.product` table
- It deletes records from these tables `cubedash.region`, `cubedash.time_overview`, `cubedash.product`.

## Delete ODC Product from ODC DB (`delete_odc_product.sql`)

- This script will delete a product and all datasets from an ODC DB.
- It will delete lineage records from the table `agdc.dataset_source`.
- It will delete location records from the table `agdc.dataset_location`.
- It deletes dataset records from the table `agdc.dataset`.
- It deletes the product from the table `agdc.dataset_type`.
- It also deletes indexes and view created for that ODC product.

Note: The `delete_odc_product.sql` is sourced from [here](https://gist.github.com/omad/1ae3463a123f37a9acf37213bebfde86) and additional script to delete index and view are added.


## Cleanup explorer from ODC DB (`cleanup_explorer.sql`)

- It deletes records from these tables `cubedash.dataset_spatial` for all dataset_type deleted from ODC DB
- Then it refreshes materialised view `cubedash.mv_dataset_spatial_quality` as this materialized view directly derives off `cubedash.dataset_spatial`

## Cleanup residual indexes from ODC DB (`cleanup_odc_indexes.sql`)

- It deletes indexes from `pg_indexes` for all dataset_type deleted from ODC DB

## Steps to run scripts in sequence

First, run `delete_odc_product_ows.sql` (optional: this step is not required if the product has not been added to OWS).

``` bash
psql -v product_name=<product-to-delete> -f delete_odc_product_ows.sql -h <database-hostname> <dbname>
```

Next run `delete_odc_product_explorer.sql` to delete products from Explorer DB.

``` bash
psql -v product_name=<product-to-delete> -f delete_odc_product_explorer.sql -h <database-hostname> <dbname>
```

Finally run `delete_odc_product.sql` to delete the ODC product in ODC DB.

``` bash
psql -v product_name=<product-to-delete> -f delete_odc_product.sql -h <database-hostname> <dbname>
```

Run `cleanup_explorer.sql` to refresh materialized view for deleted product.

``` bash
psql -f cleanup_explorer.sql -h <database-hostname> <dbname>
```

Run `cleanup_odc_indexes.sql` to refresh materialized view for deleted product.

``` bash
psql -f cleanup_odc_indexes.sql -h <database-hostname> <dbname>
```

## You can run the script `delete_product.sh` to run all steps in sequence

Set up common environment variables

``` bash
# General
export DB_DATABASE=dbname
export DB_HOSTNAME=localhost
export DB_USERNAME=example
export DB_PASSWORD=secretexample

# Explorer
export EXPLORER_USERNAME=username
export EXPLORER_PASSWORD=explorersecret

# OWS
export OWS_USERNAME=username
export OWS_PASSWORD=owssecret

# Product
export PRODUCT_NAME=product
```

Now execute the script:

``` bash
cd odc-product-delete
./delete_product.sh
```

You will be prompted to confirm the product you're deleting.

*Note*: if your product has a child product, i.e., a product that has datasets with
your product's datasets as lineage datasets, the process will fail. Please remove
child products first.
