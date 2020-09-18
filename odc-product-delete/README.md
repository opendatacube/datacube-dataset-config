# Delete ODC Product (In beta)

- AS ODC doesn't have product deletion feature with an intention to keep an immutable history of datasets, following scripts are created to manually delete an entire ODC Product and related records in ODC, Explorer and OWS DB. 
    - `delete_odc_product_ows.sql`
    - `delete_odc_product.sql` 
    - `delete_odc_product_explorer.sql` 
  
- Use with PSQL from the command line. Each script takes <product_name> and DB credentials as an input parameter.
  
### Usage
```
psql -v product_name=<product-to-delete> -f <scriptname.sql> -h <database-hostname> <dbname>
```

## Delete ODC Product from OWS (`delete_odc_product_ows.sql`)

- Before deleting product from ODC DB, we need check if the product has been added to OWS.
- If the product has been added to OWS, tables in OWS makes a foreign key constraints with ODC table. 
- Table `agdc.dataset_type` has foreign key constraint `wms.product_ranges_id_fkey` on table `wms.product_ranges`
- Because of the foreign key constraint, deleting product in ODC DB will fail and raise following error:
```
- ERROR:  update or DELETE on table "dataset_type" violates foreign key constraint "product_ranges_id_fkey" on table "product_ranges"
- DETAIL:  Key (id)=(1) is still referenced from table "product_ranges".
```
- To avoid this, there is a need to run `delete_odc_product_ows.sql` script before running `delete_odc_product.sql`. 
- This script will delete records from tables `wms.product_ranges` and `wms.sub_product_ranges`. 

## Delete ODC Product from ODC DB (`delete_odc_product.sql`)

- This script will delete a product and all datasets from an ODC DB. 
- It will delete lineage records from the table `agdc.dataset_source`.
- It will delete location records from the table `agdc.dataset_location`.
- It deletes dataset records from the table `agdc.dataset`.
- It deletes the product from the table `agdc.dataset_type`.
- It also deletes indexes and view created for that ODC product.

Note: The `delete_odc_product.sql` is sourced from [here](https://gist.github.com/omad/1ae3463a123f37a9acf37213bebfde86) and additional script to delete index and view are added.
    

## Delete ODC Product from Explorer (`delete_odc_product_explorer.sql` )
    
- After deletion of ODC Product, records in Cubedash tables are not cleared. 
- This script will delete records related to an ODC product from the Explorer Schema in the ODC DB. 
- It deletes records from these tables `cubedash.dataset_spatial`, `cubedash.time_overview`, `cubedash.product`.
- Also, it refreshes materialised view `cubedash.mv_dataset_spatial_quality`.


## Steps to run scripts in sequence
- First, run `delete_odc_product_ows.sql` if the product has not been added to OWS.
```
psql -v product_name=<product-to-delete> -f delete_odc_product_ows.sql -h <database-hostname> <dbname>
```
- Next run `delete_odc_product.sql` to delete the ODC product in ODC DB.
```
psql -v product_name=<product-to-delete> -f delete_odc_product.sql -h <database-hostname> <dbname>
```
- Finally run `delete_odc_product_explorer.sql` to delete products from Explorer DB.
```
psql -v product_name=<product-to-delete> -f delete_odc_product_explorer.sql -h <database-hostname> <dbname>
```