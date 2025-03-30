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
class Gym(Hivemind):
    def __init__(self):
        super().__init__(default_agent_id="gym")
        self.root_dir = Path(__file__).parent

        # RLBotServer MUST BE STARTED MANUALLY!
        # ONLY start the match
        self.match_manager = MatchManager()
        self.match_manager.start_match(self.root_dir / MATCH_CONFIG_PATH, False)
        
        sleep(2)
        self.connect()
                
        
        
    def connect(self):
        rlbot_server_ip = os.environ.get("RLBOT_SERVER_IP", RLBOT_SERVER_IP)
        rlbot_server_port = int(os.environ.get("RLBOT_SERVER_PORT", RLBOT_SERVER_PORT))
        print(self._game_interface)
        
        print("SHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIT")
        try:
            self._game_interface.connect(
                wants_match_communications=True,
                wants_ball_predictions=True ,
                rlbot_server_ip=rlbot_server_ip,
                rlbot_server_port=rlbot_server_port,
            )
            print("FUCK")

        except Exception as e:
            self._logger.error("Unexpected error: %s", e)
            print("SHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIT")
    def step(self, action):
        # This method should implement the logic to step the simulation forward
        # and return the new state, reward, done, and info.
        controller = action
        for index, controller in controller.items():
            if index not in self.indices:
                self._logger.warning(
                    "Hivemind produced controller state for a bot index that is does not"
                    "control (index %s). It controls %s",
                    index,
                    ", ".join(map(str, self.indices)),
                )
            player_input = flat.PlayerInput(index, controller)
            self._game_interface.send_player_input(player_input)
        self._game_interface.handle_incoming_messages(
                blocking=True
            )
        return (self._latest_packet, self._latest_prediction)
    def reset(self):
        
        # This method should reset the simulation and return the initial state.
        
        self.match_manager.shut_down()

        self.match_manager = MatchManager()
        self.match_manager.start_match(self.root_dir / MATCH_CONFIG_PATH)
        sleep(2)
        self.connect()
        sleep(2)
        while(True):
            self._game_interface.handle_incoming_messages(
                    blocking=True
                )
            print(f"len : { len(self._latest_packet.players) }")
            if(len(self._latest_packet.players) == 6):
                break
        print("YEAHHHHH")
        sleep(3)

        return (self._latest_packet, self._latest_prediction), {"field_info" : self.field_info, "indices" : self.indices}
    def close(self):
        # This method should close the simulation and clean up any resources.
        self.match_manager.stop_match()
        self.match_manager.disconnect()
    
if __name__ == "__main__":
    from bot import MyHive
    gym = Gym()
    
    ob, info = gym.reset()
    
    print(info)
    myhive = MyHive()
    myhive.initialize(field_info = info["field_info"], indices = info["indices"])
    i = 0
    while(True):

        #print(gay)
        try:
            shit, gay = ob
            #print(gay)
            actions = myhive.get_outputs(*ob)
                
            ob = gym.step(actions)
        except Exception as e:
            print("Unexpected error: %s", e)
        if i > 3000:
            ob, info = gym.reset()
            i = 0
        else:
            if i % 1000 == 0:
                print(i)
            i = i + 1