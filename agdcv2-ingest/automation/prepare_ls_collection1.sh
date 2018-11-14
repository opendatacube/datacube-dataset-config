#!/bin/bash

# Usage:   prepare.sh original_data_path
# Example: prepare.sh /micro_cube/kenya_original_data

data_path=$1

for a in `ls -1 ${data_path}/{LE07,LC08,LT05}*.tar.gz`; do
  echo $a
  b=$(basename $a)
  c=${b%%.*}
  mkdir ${data_path}/$c;
  tar -C ${data_path}/$c -zxf $a;
  python /home/localuser/Datacube/agdc-v2/ingest/prepare_scripts/landsat_collection/usgs_ls_ard_prepare.py ${data_path}/$c;
done
