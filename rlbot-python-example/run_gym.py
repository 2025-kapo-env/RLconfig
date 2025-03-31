from pathlib import Path
import os
from rlbot.managers import MatchManager
from pathlib import Path
from time import sleep
from typing import Optional
import math
import os
from traceback import print_exc
from typing import Optional
import tqdm
import itertools

from rlbot import flat
from rlbot.interface import (
    RLBOT_SERVER_IP,
    RLBOT_SERVER_PORT,
    MsgHandlingResult,
    SocketRelay,
)
from rlbot.flat import BallAnchor, ControllerState, GamePacket
from rlbot.managers import Bot
from hivemind import Hivemind
from rlbot.flat import DesiredBallState, DesiredCarState, DesiredMatchInfo, DesiredPhysics, RotatorPartial, Vector3Partial

MATCH_CONFIG_PATH = "rlbot.toml"
RLBOT_SERVER_IP = "127.0.0.1"
RLBOT_SERVER_PORT = 23234

class Gym:
    def __init__(self):
        self.root_dir = Path(__file__).parent

        # RLBotServer MUST BE STARTED MANUALLY!
        # ONLY start the match
        self.match_manager = MatchManager()
        self.match_manager.start_match(self.root_dir / MATCH_CONFIG_PATH)
        self.connect()
        time.sleep(1)
        
    def connect(self):
        rlbot_server_ip = os.environ.get("RLBOT_SERVER_IP", RLBOT_SERVER_IP)
        rlbot_server_port = int(os.environ.get("RLBOT_SERVER_PORT", RLBOT_SERVER_PORT))
        
        self.bot1 = Hivemind("gym1")
        self.bot1.team = 0
        self.bot2 = Hivemind("gym2")
        self.bot2.team = 1
        try:
            self.bot1._game_interface.connect(
                wants_match_communications=True,
                wants_ball_predictions=True ,
                rlbot_server_ip=rlbot_server_ip,
                rlbot_server_port=rlbot_server_port,
            )
            
            self.bot2._game_interface.connect(
                wants_match_communications=True,
                wants_ball_predictions=True ,
                rlbot_server_ip=rlbot_server_ip,
                rlbot_server_port=rlbot_server_port,
            )
            
        except Exception as e:
            self._logger.error("Unexpected error: %s", e)

    def step(self, action : tuple[dict[int, ControllerState]]):
        # and return the new state, reward, done, and info.(Not implemented here)
        controller1 = action[0]
        controller2 = action[1]
        
        for index, controller1 in controller1.items():
            if index not in self.bot1.indices:
                self.bot1._logger.warning(
                    "Hivemind produced controller state for a bot index that is does not"
                    "control (index %s). It controls %s",
                    index,
                    ", ".join(map(str, self.indices)),
                )
            player_input = flat.PlayerInput(index, controller1)
            self.bot1._game_interface.send_player_input(player_input)

        for index, controller2 in controller2.items():
            if index not in self.bot2.indices:
                self.bot2._logger.warning(
                    "Hivemind produced controller state for a bot index that is does not"
                    "control (index %s). It controls %s",
                    index,
                    ", ".join(map(str, self.indices)),
                )
            player_input = flat.PlayerInput(index, controller2)
            self.bot2._game_interface.send_player_input(player_input)

        self.bot1._game_interface.handle_incoming_messages(
                blocking=True
            )
        self.bot2._game_interface.handle_incoming_messages(
                blocking=True
            )
        return (self.bot1._latest_packet, self.bot1._latest_prediction), (self.bot2._latest_packet, self.bot2._latest_prediction)
    
    def reset(self):
        car_state = {
            0: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=-2048.0, y=-2560.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=0.7853981852531433, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
            1: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=0.0, y=-4608.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=1.5707963705062866, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
            2: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=-256.0, y=-3840.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=1.5707963705062866, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
            3: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=2048.0, y=2560.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=-2.356194496154785, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
            4: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=0.0, y=4608.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=-1.5707963705062866, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
            5: DesiredCarState(
            physics=DesiredPhysics(
                location=Vector3Partial(x=256.0, y=3840.0, z=35.32999801635742),
                rotation=RotatorPartial(pitch=0.0, yaw=-1.5707963705062866, roll=0.0),
                velocity=Vector3Partial(x=0.0, y=0.0, z=-27.05099868774414),
                angular_velocity=Vector3Partial(x=0.0, y=0.0, z=0.0)
            )
            ),
        }

        ball_state = DesiredBallState(DesiredPhysics(location=Vector3Partial(0, 0, z=35.32999801635742),
                                                     velocity=Vector3Partial(0, 0, 0),
                                                     angular_velocity=Vector3Partial(0, 0, 0),
                                                        rotation=RotatorPartial(0, 0, 0)))
        self.match_manager.set_game_state(balls={0: ball_state}, cars=car_state)
        
        while True:
            self.bot1._game_interface.handle_incoming_messages(
                    blocking=True
                )
            self.bot2._game_interface.handle_incoming_messages(
                    blocking=True
                )
            if self.bot1._latest_packet is None or self.bot2._latest_packet is None:
                continue
            if len(self.bot1._latest_packet.players) == 6 and len(self.bot2._latest_packet.players) == 6:
                break
        
        return (self.bot1._latest_packet, self.bot1._latest_prediction), (self.bot2._latest_packet, self.bot2._latest_prediction), {"field_info1" : self.bot1.field_info,"field_info2" : self.bot2.field_info, "indices1" : self.bot1.indices, "indices2" : self.bot2.indices}
    
    def close(self):
        self.match_manager.stop_match()
        self.match_manager.disconnect()
    
if __name__ == "__main__":
    from agents.bot import MyAgent
    import time

    MAX_ITER = 10000
    env = Gym()
    ob1, ob2, info = env.reset()
    
    p1_agent = MyAgent(field_info = info["field_info1"], indices = info["indices1"])
    p2_agent = MyAgent(field_info = info["field_info2"], indices = info["indices2"])

    for i in tqdm.tqdm(itertools.count(), desc=""):
        action1 = p1_agent.act(*ob1)
        action2 = p2_agent.act(*ob2)

        ob1, ob2 = env.step((action1, action2))

        if i % MAX_ITER == 0:
            env.reset()