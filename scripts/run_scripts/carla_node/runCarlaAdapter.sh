#/bin/bash

localCarlaAdapterPath=$HOME/tenadev/INSTALL/carlaadapter
localTenaPath=$HOME/TENA

emAddress='192.168.55.230'
emPort='55100'

dockerInternalAddress='172.17.0.2'
localAddress='192.168.55.231'

carlaMap='Ubuntu_1222'

adapterVerbosity='1'

tenaPlatform='u1804-gcc75-64'
tenaVersion='6.0.7'

carlaDockerName='tena:carla'

sudo docker run -it --rm -p 56100:56100 -v $localCarlaAdapterPath:/home/CarlaAdapter -v $localTenaPath:/home/TENA  $carlaDockerName bash -c "cd /home/CarlaAdapter/build/src; export TENA_PLATFORM=$tenaPlatform; export TENA_HOME=/home/TENA; export TENA_VERSION=$tenaVersion; export LD_LIBRARY_PATH=/home/TENA/lib; ./CarlaAdapter -emEndpoints $emAddress:$emPort -listenEndpoints $dockerInternalAddress:56100/hostname_in_ior=$localAddress -carlaHost $localAddress -verbosity $adapterVerbosity -mapPath '$carlaMap' -timeout 60000"


