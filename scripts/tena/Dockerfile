FROM ubuntu:20.04

# Make sure that the docker container gets enough memory or the compiler will crash building the CppClient
# On macos I increased the memory available from 2.0GB to 6.0GB.  I didn't try lower than this yet.
# The settings are for the VM that runs the containers and can be accessed through the Docker UI settings.
# Click on the gear icon (Setting) | Resoures then increase the memory.
# docker build --force-rm --rm -f ./Dockerfile -t tena:carla .

RUN apt-get update && apt-get install -y wget software-properties-common && add-apt-repository ppa:ubuntu-toolchain-r/test && wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key|apt-key add - && apt-add-repository "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-9 main" && apt-get update
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
RUN apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
RUN apt update

# Added to get python2 and python2-pip
RUN add-apt-repository universe
RUN apt update

# install pip for python2
RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" apt-get install -y python2 curl openssl
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python2 get-pip.py

RUN DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" apt-get install -y cmake git build-essential clang-8 g++-7 lld-8 g++-8 ninja-build libvulkan1 python2 python3-dev python3-pip libpng-dev libtiff5-dev libjpeg-dev tzdata sed curl unzip autoconf libtool rsync libxml2-dev && pip2 install --user setuptools && pip3 install --user -Iv setuptools==47.3.1 && pip2 install --user distro && pip3 install --user distro && update-alternatives --install /usr/bin/clang++ clang++ /usr/lib/llvm-8/bin/clang++ 180 && update-alternatives --install /usr/bin/clang clang /usr/lib/llvm-8/bin/clang 180

WORKDIR /home
RUN git clone https://github.com/carla-simulator/carla.git
WORKDIR /home/carla/Examples/CppClient
RUN git checkout tags/0.9.10.1 -b voices
RUN make