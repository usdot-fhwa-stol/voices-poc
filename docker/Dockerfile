FROM ubuntu:20.04

LABEL version="0.1"
LABEL description="VOICES Docker image for Pilot 1 Event 0"

SHELL ["/bin/bash", "-ec"]

RUN apt-get clean
RUN apt-get update

WORKDIR /home/BUILD

# COPY TENA MW

COPY ./lib/TENA-MiddlewareSDK-v6.0.8.B@Product@u2004-gcc9-64-*.bin .

# COPY Combined OMs

COPY ./lib/VUG-VOICES-Combined-Distribution-v0.14.3@Product@u2004-gcc9-64-*.bin .

# COPY Console

COPY ./lib/TENA-Console-v2.0.1@Product@u2004-gcc9-64*.deb .

# COPY TDCS


# COPY ./lib/VUG-VOICES-Combined-DataCollectionDistribution-v0.14.3@Product@u2004-gcc9-64-*.deb .

# COPY DataView

# COPY ./lib/TDCS-DataView-v1.5.4@Product@u2004-gcc9-64*.deb .

# Make lib executable

RUN chmod -R a+x *.bin

# INSTALL TENA MW

RUN ./TENA-MiddlewareSDK-v6.0.8.B@Product@u2004-gcc9-64-*.bin -i /home/ --auto

# INSTALL Combined OMs

RUN ./VUG-VOICES-Combined-Distribution-v0.14.3@Product@u2004-gcc9-64-*.bin -i /home/ --auto

# INSTALL Console

USER root

RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" USER="root" apt install apt-utils

RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" USER="root" apt install -o DPkg::options::=--force-overwrite ./TENA-Console-v2.0.1@Product@u2004-gcc9-64*.deb

# INSTALL TDCS

# INSTALL DataView

# Install Boost

RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" USER="root" apt install libboost-all-dev -y

# INSTALL libxcb

RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" USER="root" apt install libxcb-xinerama0 libfreetype6 libfontconfig libsm6 libxi6 libx11-xcb-dev libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0 libjpeg8 libtiff5 -y


# COPY Start Scripts

COPY ./start_scripts /home/start_scripts


RUN chmod a+x -R /home/start_scripts


# INSTALL pip

RUN apt install python3-pip -y

# INSTALL python packages

RUN pip install -r /home/start_scripts/requirements.txt

# RUN xhost +local:docker
# RUN ldd /usr/lib/qt/plugins/platforms/libqxcb.so
# Cleanup

RUN apt-get -qy autoremove

RUN chmod a+rw /opt/TENA



# COPY CARLA TENA Adapter

RUN mkdir /home/INSTALL

COPY ./lib/CARLAtenaAdapter-1.4.4 /home/INSTALL

# CMD
# - run CARLA
# - run CARLA adapter
# - option to run and collect TDCS? 
# - option to run console

# COPY CARLA

# COPY ./lib/CARLA_0.9.10.1.tar.gz .

RUN mkdir /home/CARLA_0.9.10.1

COPY ./lib/CARLA_0.9.10.1/PythonAPI /home/CARLA_0.9.10.1

# RUN tar -xzvf CARLA_0.9.10.1.tar.gz -C /home/CARLA_0.9.10.1

RUN echo 'source /home/start_scripts/setup-docker.sh' >> /root/.bashrc


# CMD ["tail","-f","/dev/null"]
