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

set search_path = 'agdc';

-- Select the current list of dataset_type (product) names and compare to
-- the list of index names to identify the residue indexes with deleted dataset_type
-- then finally delete any indexes that are still in the database for the deleted product
WITH residue_index_name AS ( WITH index_p_name AS
(
                SELECT DISTINCT Substring(indexname, '^dix_(.*?)_(lat_lon_time|instrument|platform|time_lat_lon)$') AS index_name_wt_suffix
                FROM            pg_indexes
                WHERE           indexname LIKE any (array['dix_%_lat_lon_time', 'dix_%_instrument', 'dix_%_platform', 'dix_%_time_lat_lon']))
SELECT index_name_wt_suffix
FROM   index_p_name
WHERE  index_name_wt_suffix NOT IN
       (
              SELECT NAME
              FROM   agdc.dataset_type))
SELECT FORMAT('DROP INDEX CONCURRENTLY %I.%I;', schemaname, indexname) as drop_statement
FROM   pg_indexes
WHERE  tablename='dataset'
AND    indexname LIKE ANY
       (
              SELECT concat ('dix_', index_name_wt_suffix, '%')
              FROM   residue_index_name);  \gexec