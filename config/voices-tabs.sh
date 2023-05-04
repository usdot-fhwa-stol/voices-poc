#!/bin/bash

## VOICES-1

# em

# tdcs
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-log-collection.sh

# sp
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-scenario-publisher.sh

# econolite
~/econolite-vtsc$ python3 eos_test.py
https://127.0.0.1:8443/

# msg
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-tj2735-message-adapter.sh | tee ~/voices-poc/logs/tj2735-message-adapter

# tleg
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-traffic-light-entity-generator.sh | tee ~/voices-poc/logs/start-traffic-light-entity-generator.sh

# carla
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-carla.sh --map smart_intersection

# opencda
~/voices-poc/scripts/carla_python_scripts/opencda$ ./start-opencda-car.sh

# carla-tena
~/voices-poc/scripts/run_scripts/pilot1/src$ ./start-carla-tena-adapter.sh



## VOICES-2


em

voices-poc
tdcs
sp
carma
carla
carla-tena-adapter
tj2735
tleg
ros
build



