#!/bin/bash

# Usage:   prepare.sh original_data_path
# Example: prepare.sh /micro_cube/kenya_original_data

data_path=$1

for a in `ls -1 ${data_path}/LT5*.tar.gz`; do
  echo $a

  mkdir ${data_path}/temp_lt5;
  tar -C ${data_path}/temp_lt5 -zxf $a;

  sceneid=`ls -1 ${data_path}/temp_lt5 | head -n 1 | grep -o 'LT5[0-9A-Z]\+\?'`;
  echo ${sceneid};

  mkdir ${data_path}/${sceneid}
  mv ${data_path}/temp_lt5/* ${data_path}/${sceneid};

  python /home/localuser/Datacube/agdc-v2/ingest/prepare_scripts/usgslsprepare.py ${data_path}/${sceneid};
  rm -r ${data_path}/temp_lt5;

done
