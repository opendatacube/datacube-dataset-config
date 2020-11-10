----------------------------------------------------------
-- SQL to DELETE a Data Cube Product in Explorer
----------------------------------------------------------

--
-- Use with psql from the command line:
--
-- psql -v product_name=<product-to-DELETE> -f delete_product_ows.sql -h <database-hostname> <dbname>
--

--
-- After deletion of Data Cube Product, records in Cubedash tables are not cleared. Following queries will keep Explorer clean.
--

--
-- SELECT/DELETE PRODUCT RECORDS FROM CUBEDASH TABLES
--

--
-- for explorer version with region support
--
DELETE FROM cubedash.region WHERE dataset_type_ref=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');


--
-- delete main product
--
SELECT count(*) FROM cubedash.time_overview WHERE product_ref=(SELECT id FROM cubedash.product WHERE name = :'product_name');

DELETE FROM cubedash.time_overview WHERE product_ref=(SELECT id FROM cubedash.product WHERE name = :'product_name');

SELECT count(*) FROM cubedash.product WHERE name = :'product_name';

DELETE FROM cubedash.product WHERE name = :'product_name';

--
-- remove lineage bond product from derived_product_refs
--
UPDATE cubedash.product
SET    derived_product_refs = array_remove(derived_product_refs, (
       (
              SELECT id::smallint
              FROM   agdc.dataset_type
              WHERE  NAME=:'product_name')));

--
-- delete lineage bond product from source_product_refs
--
UPDATE cubedash.product
SET    source_product_refs = array_remove(source_product_refs, (
       (
              SELECT id::smallint
              FROM   agdc.dataset_type
              WHERE  NAME=:'product_name')));
