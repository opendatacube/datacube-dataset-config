--------------------------------------
-- SQL to Delete a Data Cube Product
--------------------------------------
--
-- Use with psql from the command line:
--
-- psql -v product_name=<product-to-delete> -f delete_odc_product.sql -h <database-hostname> <dbname>
--

--
-- COUNT NUMBER OF DATASETS OF EACH TYPE (including archived)
--
-- select
--   count(*),
--   t.name
-- from dataset
--   left join dataset_type t on dataset.dataset_type_ref = t.id
-- group by t.name;

--
-- CHECK FOR LINEAGE RECORDS
--

-- Are there any datasets that are descendents of this product?
-- If so, they will need to be removed first!

set search_path = 'agdc';

select count(*)
from dataset_source
  left join dataset d on dataset_source.source_dataset_ref = d.id
where d.dataset_type_ref = (select id
                            from dataset_type
                            where dataset_type.name = :'product_name');

-- Are there any lineage records which need deleting?
-- These are the lineage history of the product we're deleting.
select count(*)
from dataset_source
  left join dataset d on dataset_source.dataset_ref = d.id
where d.dataset_type_ref = (select id
                            from dataset_type
                            where dataset_type.name = :'product_name');
--
-- DELETE LINEAGE RECORDS
--
WITH datasets as (SELECT id
                  FROM dataset
                  where dataset.dataset_type_ref = (select id
                                                    FROM dataset_type
                                                    WHERE name = :'product_name'))
DELETE FROM dataset_source
USING datasets
where dataset_source.dataset_ref = datasets.id;


--
-- CHECK FOR LOCATION RECORDS
--
select count(*)
from dataset_location
  left join dataset d on dataset_location.dataset_ref = d.id
where d.dataset_type_ref = (select id
                            from dataset_type
                            where dataset_type.name = :'product_name');


WITH datasets as (SELECT id
                  FROM dataset
                  where dataset.dataset_type_ref = (select id
                                                    FROM dataset_type
                                                    WHERE name = :'product_name'))
select count(*)
from dataset_location, datasets
where dataset_location.dataset_ref  = datasets.id;


--
-- DELETE LOCATION RECORDS
--
WITH datasets as (SELECT id
                  FROM dataset
                  where dataset.dataset_type_ref = (select id
                                                    FROM dataset_type
                                                    WHERE name = :'product_name'))
DELETE FROM dataset_location
USING datasets
where dataset_location.dataset_ref = datasets.id;

--
-- DELETE DATASET RECORDS
--
DELETE FROM dataset
where dataset.dataset_type_ref = (select id
                            from dataset_type
                            where dataset_type.name = :'product_name');


--
-- FINALLY, DELETE THE PRODUCT
--
DELETE FROM dataset_type
where dataset_type.name = :'product_name';


--
-- DROP VIEW
--
\set view_name 'dv_' :product_name '_dataset'

DROP VIEW IF EXISTS :view_name;


--
-- DROP DYNAMIC INDEXES FROM 'dataset' table
--
\set index_name 'dix_' :product_name '_%'

SELECT FORMAT('DROP INDEX CONCURRENTLY %I.%I;', schemaname, indexname) as drop_statement from pg_indexes where tablename ='dataset' and indexname like :'index_name'; \gexec