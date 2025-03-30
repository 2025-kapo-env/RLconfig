from pathlib import Path
import os
from rlbot.managers import MatchManager
from pathlib import Path
from time import sleep
from typing import Optional

import os
from traceback import print_exc
from typing import Optional

from rlbot import flat
from rlbot.interface import (
    RLBOT_SERVER_IP,
    RLBOT_SERVER_PORT,
    MsgHandlingResult,
    SocketRelay,
)
from rlbot.flat import BallAnchor, ControllerState, GamePacket
from rlbot.managers import Bot, Hivemind

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
                
        
        
    def connect(self):
        rlbot_server_ip = os.environ.get("RLBOT_SERVER_IP", RLBOT_SERVER_IP)
        rlbot_server_port = int(os.environ.get("RLBOT_SERVER_PORT", RLBOT_SERVER_PORT))
        
        self.bot1 = Hivemind("gym1")
        self.bot2 = Hivemind("gym2")
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
            self.bot1._try_initialize() # IDK if this is needed
            self.bot2._try_initialize()
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
        
        self.match_manager.shut_down()
        self.match_manager = MatchManager()
        self.match_manager.start_match(self.root_dir / MATCH_CONFIG_PATH)
        
        self.connect()
        while(True):
            self.bot1._game_interface.handle_incoming_messages(
                    blocking=True
                )
            self.bot2._game_interface.handle_incoming_messages(
                    blocking=True
                )
            if(self.bot1._latest_packet is None or self.bot2._latest_packet is None):
                continue
            if(len(self.bot1._latest_packet.players) == 6 and len(self.bot2._latest_packet.players) == 6):
                break
        
        return (self.bot1._latest_packet, self.bot1._latest_prediction), (self.bot2._latest_packet, self.bot2._latest_prediction), {"field_info" : self.bot1.field_info, "indices1" : self.bot1.indices, "indices2" : self.bot1.indices}
    def close(self):
        self.match_manager.stop_match()
        self.match_manager.disconnect()
    
if __name__ == "__main__":
    from bot import MyHive
    gym = Gym()
    
    ob1,ob2, info = gym.reset()
    
    #print(info)
    myhive, ophive = MyHive(), MyHive()
    myhive.initialize(field_info = info["field_info"], indices = info["indices1"])
    ophive.initialize(field_info = info["field_info"], indices = info["indices2"])
    i = 0
    while(True):
        try:
            action1 = myhive.get_outputs(*ob1)
            action2 = ophive.get_outputs(*ob2)
            
            actions = (action1, action2)
            #print(actions)
            ob1,ob2 = gym.step(actions)
        except Exception as e:
            print("Unexpected error: %s" % e)
            print_exc()
        if i > 2000:
            ob1,ob2, info = gym.reset()
            i = 0
        else:
            if i % 1000 == 0:
                print(int(i / 1000))
            i = i + 1