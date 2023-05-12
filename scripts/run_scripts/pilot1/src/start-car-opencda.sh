#!/bin/bash

. ../../../../config/node_info.config

echo
echo "!!!*** Run \`conda activate opencda\` before starting this script ***!!!"
echo

openCdaCarName=smart_intersection_test_4

cp ../../../carla_python_scripts/opencda/$openCdaCarName.py $openCdaPath/opencda/scenario_testing/
cp ../../../carla_python_scripts/opencda/$openCdaCarName.yaml $openCdaPath/opencda/scenario_testing/config_yaml/

( cd $openCdaPath; python opencda.py -t $openCdaCarName --apply_ml)
