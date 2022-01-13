#!/bin/bash

tenadevDir=$HOME/tenadev/INSTALL

emAddress='192.168.55.230'
emPort='55100'

localAddress='192.168.55.230'

adapterVerbosity='4'

$tenadevDir/entitygenerator/build/src/EntityGenerator -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -verbosity $adapterVerbosity
