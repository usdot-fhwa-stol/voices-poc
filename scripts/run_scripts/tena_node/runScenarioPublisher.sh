#!/bin/bash

tenadevDir=$HOME/tenadev/INSTALL

scenarioFile=$HOME/voices-poc/scenario_files/demo0-scenario.xml

emAddress='192.168.55.230'
emPort='55100'

localAddress='192.168.55.230'

adapterVerbosity='4'

$tenadevDir/scenario-publisher/build/src/scenario-publisher -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -scenarioFile $scenarioFile -verbosity $adapterVerbosity
