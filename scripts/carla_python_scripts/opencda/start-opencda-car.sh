#!/bin/bash

OPENCDATEST=smart_intersection_test_4
OPENCDADIR=~/OpenCDA

cp $OPENCDATEST.py $OPENCDADIR/opencda/scenario_testing/
cp $OPENCDATEST.yaml $OPENCDADIR/opencda/scenario_testing/config_yaml/

( cd $OPENCDADIR; conda activate opencda; python opencda.py -t $OPENCDATEST )