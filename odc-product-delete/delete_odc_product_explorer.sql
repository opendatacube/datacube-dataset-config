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

SELECT count(*) FROM cubedash.dataset_spatial WHERE dataset_type_ref=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

DELETE FROM cubedash.dataset_spatial WHERE dataset_type_ref=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');


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
-- delete lineage bond product
--
SELECT Count(*)
FROM   cubedash.time_overview
WHERE  product_ref in
       (
              SELECT id
              from   cubedash.product
              WHERE  (
                            SELECT id
                            FROM   agdc.dataset_type
                            WHERE  NAME=:'product_name') = ANY (derived_product_refs)
              OR
                     (
                            SELECT id
                            FROM   agdc.dataset_type
                            WHERE  NAME=:'product_name') = ANY (source_product_refs)
       );

DELETE
FROM   cubedash.time_overview
WHERE  product_ref in
       (
              SELECT id
              from   cubedash.product
              WHERE  (
                            SELECT id
                            FROM   agdc.dataset_type
                            WHERE  NAME=:'product_name') = ANY (derived_product_refs)
              OR
                     (
                            SELECT id
                            FROM   agdc.dataset_type
                            WHERE  NAME=:'product_name') = ANY (source_product_refs)
       );

DELETE
FROM   cubedash.product
WHERE  (
              SELECT id
              FROM   agdc.dataset_type
              WHERE  NAME=:'product_name') = ANY (derived_product_refs)
OR
       (
              SELECT id
              FROM   agdc.dataset_type
              WHERE  NAME=:'product_name') = ANY (source_product_refs);



SELECT count(*) FROM cubedash.mv_dataset_spatial_quality WHERE dataset_type_ref=(SELECT id FROM agdc.dataset_type WHERE name=:'product_name');

REFRESH MATERIALIZED VIEW CONCURRENTLY cubedash.mv_dataset_spatial_quality;