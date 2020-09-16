----------------------------------------------------------
-- SQL to DELETE a Data Cube Product in OWS
----------------------------------------------------------

--
-- Use with psql from the command line:
--
-- psql -v product_name=<product-to-DELETE> -f delete_product_ows.sql -h <database-hostname> <dbname>
--
--
-- Running delete_odc_product.sql (https://gist.github.com/omad/1ae3463a123f37a9acf37213bebfde86) to delete Data Cube Product fails
-- when the product has been added in OWS since OWS maintains a foreign key to ODC
-- psql:DELETE_odc_product.sql:103:
-- ERROR:  update or DELETE on table "dataset_type" violates foreign key constraint "product_ranges_id_fkey" on table "product_ranges"
-- DETAIL:  Key (id)=(1) is still referenced from table "product_ranges".
--
--To fix the above issue, following queries need to be run before Product deletion.
--
-- SELECT/DELETE PRODUCT RECORDS FROM TABLE PRODUCT/SUB PRODUCT RANGES


SELECT count(*) FROM wms.product_ranges WHERE id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

DELETE FROM wms.product_ranges WHERE id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');


SELECT count(*) FROM wms.sub_product_ranges WHERE product_id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

DELETE FROM wms.sub_product_ranges WHERE product_id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');
