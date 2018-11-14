#!/bin/bash

# Usage:   ingest.sh original_data_path dataset_type ingestion_config
# Example: ingest.sh /micro_cube/kenya_original_data ls7_ledaps_scene ingestion_configs/ls7_sr_scenes_wgs84_kenya.yaml

start_time=$(date)

echo ${start_time}

data_path=$1

for scene_path in `ls -d ${data_path}/*/`; do
  echo ${scene_path};
  datacube dataset add --dtype $2 ${scene_path};
done

datacube -v ingest -c $3 --executor multiproc 8

end_time=$(date)
echo "Ingestion was started at ${start_time}"
echo "Ingestion completed at ${end_time}"
