----------------------------------------------------------
-- SQL to CLEANUP ODC Dynamic Indexes
----------------------------------------------------------

--
-- Use with psql from the command line:
--
-- psql -f cleanup_odc_indexes.sql -h <database-hostname> <dbname>
--

--
-- Run as required to cleanup all left-over dynamic indexes
--

-- delete all entry from dataset_spatial where dataset_type_ref has been deleted in agdc
set search_path = 'agdc';

SELECT name FROM datset_type;

SELECT format('div_%I_%s', (select name from agdc.dataset_type limit 1), '%');

select pgi.indexname from pg_indexes pgi WHERE pgi.indexname ~ (SELECT name from agdc.dataset_type limit 1);

select substring(indexname, '^dix_(.*?)_lat_lon_time$') from pg_indexes pgi WHERE pgi.indexname LIKE 'dix_%_lat_lon_time';

select name from agdc.dataset_type where name IN (select substring(indexname, '^dix_(.*?)_lat_lon_time$') as index_p_name from pg_indexes pgi WHERE pgi.indexname LIKE 'dix_%_lat_lon_time');

with index_p_name as (select substring(indexname, '^dix_(.*?)_lat_lon_time$') as name from pg_indexes WHERE indexname LIKE 'dix_%_lat_lon_time') select name from index_p_name where name not in (select name from agdc.dataset_type);

with index_p_name as (select substring(indexname, '^dix_(.*?)_instrument$') as name from pg_indexes WHERE indexname LIKE 'dix_%_instrument') select name from index_p_name where name not in (select name from agdc.dataset_type);

with index_p_name as (select substring(indexname, '^dix_(.*?)_platform$') as name from pg_indexes WHERE indexname LIKE 'dix_%_platform') select name from index_p_name where name not in (select name from agdc.dataset_type);

with index_p_name as (select substring(indexname, '^dix_(.*?)_time_lat_lon$') as name from pg_indexes WHERE indexname LIKE 'dix_%_time_lat_lon') select name from index_p_name where name not in (select name from agdc.dataset_type);

with viewcheck as (select substring(viewname, '^dv_(.*?)_dataset$') as vname from pg_catalog.pg_views where viewname LIKE 'dv_%_dataset') select vname from viewcheck where vname not in (select name from agdc.dataset_type);