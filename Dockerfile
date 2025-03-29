FROM env/cudagl:12.4.0-devel-ubuntu22.04
WORKDIR /root

RUN apt update && apt install -y \
    curl software-properties-common git xvfb scrot vim \
    mesa-utils libgl1-mesa-dri libglx-mesa0 \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y \
        python3.11 python3.11-venv python3.11-dev python3-pip wine \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3

RUN git clone https://github.com/derrod/legendary.git \
    && cd legendary \
    && python3 -m pip install -U . \
    && echo 'export PATH=$PATH:~/.local/bin' >> ~/.profile \
    && . ~/.profile


ENV XAUTHORITY=/root/.Xauthority
RUN apt update && apt install -y \
    x11-apps \
    xauth \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install -y wget
# RUN wget -q -O- https://packagecloud.io/dcommander/virtualgl/gpgkey > gpgkey
# RUN gpg --dearmor --yes -o /etc/apt/trusted.gpg.d/VirtualGL.gpg gpgkey
# RUN echo "deb [signed-by=/etc/apt/trusted.gpg.d/VirtualGL.gpg] https://packagecloud.io/dcommander/virtualgl/any/ any main" | tee /etc/apt/sources.list.d/virtualgl.list
# RUN apt-get update
# RUN apt-get install -y virtualgl

CMD bash -c "\
    cd rlbot-python-example && pip install -r requirements.txt && \
    curl -L -o RLBotServer https://github.com/RLBot/core/releases/download/v0.4.4/RLBotServer && \
    exec bash"