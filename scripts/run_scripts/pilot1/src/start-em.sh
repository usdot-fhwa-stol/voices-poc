#!/bin/bash

#.231 /opt/TENA/Console-v2.0.0.Beta3$ 

/home/carma/tenadev/u2004-gcc9-64/TENA/executionManager-v6.0.8.2/bin/executionManager  -listenendpoints 192.168.55.231:55100 -logDir /home/carma/tenadev/u2004-gcc9-64/TENA/executionManager-v6.0.8.2/log -recoveryDir /home/carma/tenadev/u2004-gcc9-64/TENA/executionManager-v6.0.8.2/save -connectionTimeoutInMilliseconds 10000 -twowayTimeoutInMilliseconds 20000 -transientCommunicationAttempts 3 -disconnectTimeoutInMilliseconds 5000

