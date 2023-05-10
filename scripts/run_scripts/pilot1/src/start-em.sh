#!/bin/bash

# Start Execution Manager

. ../../../../config/node_info.config

$tenaExecutionManagerPath/bin/executionManager \
    -listenendpoints $localAddress:55100 \
    -logDir $tenaExecutionManagerPath/log \
    -recoveryDir $tenaExecutionManagerPath/save \
    -connectionTimeoutInMilliseconds 10000 -twowayTimeoutInMilliseconds 20000 \
    -transientCommunicationAttempts 3 -disconnectTimeoutInMilliseconds 5000
