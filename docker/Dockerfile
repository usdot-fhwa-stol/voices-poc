#
# BUILD COMMAND: sudo DOCKER_BUILDKIT=1 docker build -t voices:0.0.1 . --progress=plain
#

FROM ubuntu:20.04

LABEL version="0.0.1"
LABEL description="VOICES Docker image for Pilot 1 Event 0"

SHELL ["/bin/bash", "-ec"]

USER root
ARG DEBIAN_FRONTEND="noninteractive" 
ARG TZ="America/New_York"
ARG USER="root"

WORKDIR /home

# INSTALL TENA bin

RUN --mount=type=bind,target=/home/BUILD,readonly,source=lib/BUILD \
    /home/BUILD/TENA-MiddlewareSDK-v6.0.8.B@Product@u2004-gcc9-64-*.bin -i /home/ --auto && \
    # /home/BUILD/VUG-VOICES-Combined-Distribution-v0.14.4@Product@u2004-gcc9-64-*.bin -i /home/ --auto && \
    rm -rf /tmp/*

# INSTALL TDCS

# INSTALL DataView

# INSTALL Console

RUN --mount=type=bind,target=/home/BUILD,readonly,source=lib/BUILD \
    apt install -o DPkg::options::=--force-overwrite \
    /home/BUILD/TENA-Console-v2.0.1@Product@u2004-gcc9-64-*.deb \
    # /home/BUILD/VUG-VOICES-Combined-DataCollectionDistribution-v0.14.4@Product@u2004-gcc9-64-*.deb \
    /home/BUILD/TDCS-DataView-v1.5.4@Product@u2004-gcc9-64-*.deb && \
    # Fix permissions for installed TENA apps
    chmod -R a+rw /opt/TENA

# INSTALL apt packages 

RUN apt-get update && apt install -y \
    # install apt utils for installing packages (mostly for TENA console)
    apt-utils \
    # install boost
    libboost-all-dev \
    # install qt packages
    libxcb-xinerama0 libfreetype6 libfontconfig libsm6 libxi6 libx11-xcb-dev libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0 libjpeg8 libtiff5 \
    # install pip
    python3-pip \
    # install debug tools
    iputils-ping nano \
    # cleanup apt lists
    && rm -rf /var/lib/apt/lists/*

# INSTALL python packages

RUN pip install numpy pandas pygame pycrate && \
    rm -rf /root/.cache
RUN ls -l

COPY ./lib/COPY /home

# COPY Start Scripts

RUN chmod a+x -R /home/start_scripts/

# CLEANUP

RUN rm -rf /home/BUILD /tmp/* && \
    apt-get -qy autoremove

# CMD
# - run CARLA
# - run CARLA adapter
# - option to run and collect TDCS? 
# - option to run console

RUN echo 'source /home/start_scripts/setup-docker.sh' >> /root/.bashrc


CMD ["/bin/bash","-l","-c","/home/start_scripts/startup-apps.sh"]
