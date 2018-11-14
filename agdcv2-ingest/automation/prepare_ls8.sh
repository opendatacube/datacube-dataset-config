#!/bin/bash

# Usage:   prepare.sh original_data_path
# Example: prepare.sh /micro_cube/kenya_original_data

data_path=$1

for a in `ls -1 ${data_path}/LC8*.tar.gz`; do
  echo $a

  mkdir ${data_path}/temp_ls8;
  tar -C ${data_path}/temp_ls8 -zxf $a;

  sceneid=`ls -1 ${data_path}/temp_ls8 | head -n 1 | grep -o 'LC8[0-9A-Z]\+\?'`;
  echo ${sceneid};

  mkdir ${data_path}/${sceneid}
  mv ${data_path}/temp_ls8/* ${data_path}/${sceneid};

  python /home/localuser/Datacube/agdc-v2/ingest/prepare_scripts/usgslsprepare.py ${data_path}/${sceneid};
  rm -r ${data_path}/temp_ls8;

done
