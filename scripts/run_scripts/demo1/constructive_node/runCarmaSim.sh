#!/bin/bash
trap cleanup SIGINT

function cleanup {
	echo "Stopping CARMA Simulation"
	docker kill carla_carma_integration
	pkill -9 CarlaUE4
	exit
}

. ../node_info.config

if [[ $carmaID == "CARMA-TFHRC" ]]
then
       SPAWN_PT="-195.3, -503.3, 38, 0, 0, 55"
elif [[ $carmaID == "CARMA-SPR" ]]
then
       SPAWN_PT="-189.9, -508.5, 38, 0, 0, 38"
elif [[ $carmaID == "CARMA-MITRE" ]]
then
       SPAWN_PT="-195.3, -503.3, 38, 0, 0, 55"
elif [[ $carmaID == "CARMA-AUG" ]]
then
       SPAWN_PT="-182.6, -511.5, 38, 0, 0, 18"
fi

#VEH_4="131.3, -427.6, 40, 0, 0, 192" #38.955004, -77.147543 Virtual
#VEH_5="-195.3, -503.3, 38, 0, 0, 55" #38.955693, -77.151303 Constructed #Mitre
#VEH_3="-189.9, -508.5, 38, 0, 0, 38" #38.955737, -77.151238 Constructed #Springfield/voices-2
#VEH_2="-182.6, -511.5, 38, 0, 0, 18" #38.955761, -77.151152 Constructed #Augusta/voices-1
#VEH_1="-174.9, -513.0, 38, 0, 0, 10" #Live

mkdir -p $localCarmaSimLogPath

CARLA_LOG=$localCarmaSimLogPath/voices_carla_simulator.log
SIM_LOG=$localCarmaSimLogPath/voices_carla_carma_integration.log

echo "" >> $CARLA_LOG
echo "<< ***** New Session **** >>" >> $CARLA_LOG
date >> $CARLA_LOG
echo "" >> $SIM_LOG
echo "<< ***** New Session **** >>" >> $SIM_LOG
date >> $SIM_LOG


$localCarlaPath/CarlaUE4.sh &>> $CARLA_LOG &
sleep 5

#python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py


docker run \
	   -it -d --rm \
       --name carla_carma_integration \
       --net=host \
       usdotfhwastol/carma-carla-integration:carma-carla-1.0.0-voices-color \

docker exec \
       -it \
       carla_carma_integration \
       bash -c \
       "export PYTHONPATH=$PYTHONPATH:/home/PythonAPI/carla-0.9.10-py2.7-linux-x86_64.egg &&
       source /home/carla_carma_ws/devel/setup.bash && 
       roslaunch carla_carma_agent carla_carma_agent.launch town:=\"$carlaMapName\" vehicle_color_ind:=\"0\" spawn_point:=\"$SPAWN_PT\"" &>> $SIM_LOG

cleanup

       

