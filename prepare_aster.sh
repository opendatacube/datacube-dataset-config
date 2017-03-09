#!/bin/bash

# Usage:   prepare.sh original_data_path
# Example: prepare.sh /micro_cube/kenya_original_data

data_path=$1

for a in `ls -1 ${data_path}/*.zip`; do
  #echo $a

  #mkdir ${data_path}/temp;
  #unzip $a -d ${data_path}/temp;

  sceneid=`ls -1 ${data_path}/ | head -n 1 | grep -o 'ASTGTM2_[0-9A-Z]\+\?'`;
  echo ${sceneid};

  #mkdir ${data_path}/${sceneid}
  #mv ${data_path}/temp/* ${data_path}/${sceneid};
  #chmod 777 ${data_path}/${sceneid}
  python /home/localuser/Datacube/ingest/prepare_scripts/aster_gdem2_prepare.py -p ${data_path}/${sceneid};
  #datacube -v dataset add -t terra_aster_gdm_v2_scene ${data_path}/${sceneid}/*.yaml
  #rm -r ${data_path}/temp;

done
