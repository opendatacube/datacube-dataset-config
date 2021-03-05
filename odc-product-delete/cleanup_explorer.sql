----------------------------------------------------------
-- SQL to CLEANUP Explorer
----------------------------------------------------------

--
-- Use with psql from the command line:
--
-- psql -f cleanup_explorer.sql -h <database-hostname> <dbname>
--

--
-- After deletion of Data Cube Product, records in Cubedash tables are not cleared. Following queries will keep Explorer clean.
--

-- delete all entry from dataset_spatial where dataset_type_ref has been deleted in agdc
delete from cubedash.dataset_spatial where not exists (select id from agdc.dataset_type where id = dataset_type_ref);

-- cubedash.mv_dataset_spatial_quality is directly derived from cubedash.dataset_spatial
-- run this straight after the deletion
REFRESH MATERIALIZED VIEW CONCURRENTLY cubedash.mv_dataset_spatial_quality;