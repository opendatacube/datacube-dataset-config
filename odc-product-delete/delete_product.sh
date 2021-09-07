#! /usr/bin/env bash

# Caution: ensure child products are removed first

read -p "Are you sure you want to delete product ${PRODUCT_NAME}? (Y to continue): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

# Delete from Explorer
PGPASSWORD=$EXPLORER_PASSWORD psql -U $EXPLORER_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
  -f delete_odc_product_explorer.sql -v product_name=$PRODUCT_NAME

# Delete from OWS
PGPASSWORD=$OWS_PASSWORD psql -U $OWS_USERNAME -d $DB_DATABASE -h $DB_HOSTNAME \
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
