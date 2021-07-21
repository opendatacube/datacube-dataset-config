#! /usr/bin/env bash

# Caution: ensure child products are removed first

# Delete from Explorer
PGPASSWORD=$EXPLORER_PASSWORD psql -U $EXPLORER_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f delete_odc_product_explorer.sql -v product_name=$PRODUCT_NAME

# Delete from OWS
PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f delete_odc_product_ows.sql -v product_name=$PRODUCT_NAME

# Delete from ODC
PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f delete_odc_product.sql -v product_name=$PRODUCT_NAME

# Clean up Explorer views
PGPASSWORD=$EXPLORER_PASSWORD psql -U $EXPLORER_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f cleanup_explorer.sql -v product_name=$PRODUCT_NAME

# Clean up ODC indexes
PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f cleanup_odc_indexes.sql -v product_name=$PRODUCT_NAME
