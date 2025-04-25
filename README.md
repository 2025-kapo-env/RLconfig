# Rocket League RL Environment Setup Guide

## 1. Install Legendary and Download the Game
```bash
git clone https://github.com/derrod/legendary.git
cd legendary
pip install .
echo 'export PATH=$PATH:~/.local/bin' >> ~/.profile && source ~/.profile
legendary install "RocketLeague"
```

## 2. Download RLBot server
- Download RLBotServer from https://github.com/RLBot/core/releases/tag/v0.4.10.
- Place RLBotServer in the `./rlbot-python-example` directory.

## 3. Build Docker Image
```bash
sudo bash cudagl_build.sh -d --image-name env/cudagl --cuda-version 12.4.0 --os ubuntu --os-version 22.04 --arch x86_64 --cudagl
docker build -t rlenv .
```
## 4. Run the Docker Container
```bash
xhost +local:docker
docker run -it --gpus all \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/Games:/Games \
  -v /wine:/wine \
  -v ~/.Xauthority:/root/.Xauthority \
  -v ./rlbot-python-example:/root/rlbot-python-example \
  --network host rlenv
```
## 5. Authorize Legendary & Run RLBot
```bash
winecfg # turn on graphics emulator
legendary auth
legendary import Sugar /Games/rocketleague
# legendary update RocketLeague
# legendary launch rocketleague
python3 run.py
```
