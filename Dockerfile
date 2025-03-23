FROM env/cudagl:12.4.0-devel-ubuntu22.04
WORKDIR /root

RUN apt update && apt install -y \
    curl software-properties-common git xvfb scrot vim \
    mesa-utils libgl1-mesa-dri libglx-mesa0 \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y \
        python3.11 python3.11-venv python3.11-dev python3-pip wine64 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3

RUN git clone https://github.com/derrod/legendary.git \
    && cd legendary \
    && python3 -m pip install -U . \
    && echo 'export PATH=$PATH:~/.local/bin' >> ~/.profile \
    && . ~/.profile

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get -y install wine32 winbind

RUN cd rlbot-python-example && pip install -r requirements.txt
RUN curl -L -o RLBotServer https://github.com/RLBot/core/releases/download/v0.4.4/RLBotServer

ENV XAUTHORITY=/root/.Xauthority
RUN apt update && apt install -y \
    x11-apps \
    xauth \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*
    
CMD ["bash"]