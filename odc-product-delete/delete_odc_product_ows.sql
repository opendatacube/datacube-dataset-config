----------------------------------------------------------
-- SQL to DELETE a Data Cube Product in OWS
----------------------------------------------------------

--
-- Use with psql from the command line:
--
-- psql -v product_name=<product-to-DELETE> -f delete_odc_product_ows.sql -h <database-hostname> <dbname>
--
-- SELECT/DELETE PRODUCT RECORDS FROM TABLE PRODUCT/SUB PRODUCT RANGES
--

SELECT count(*) FROM wms.product_ranges WHERE id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

DELETE FROM wms.product_ranges WHERE id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');


SELECT count(*) FROM wms.sub_product_ranges WHERE product_id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

DELETE FROM wms.sub_product_ranges WHERE product_id=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');