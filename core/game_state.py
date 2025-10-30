
import json
from card_actions.card_base import Card

class GameState:
    def __init__(self, game_manager,):
        print("DEBUG: GameState __init__ starting")
        self.game_manager = game_manager
        self.rule_state = None
        self.battlefield = []
        self.players = {}
        self.turn = 0
        self.stack = []
        self.log = []
        self.trigger_manager = None   #will be injected during game setup
        print("DEBUG: GameState __init__ complete")

    def add_player(self, player_state):
        self.players[player_state.name] = player_state

    def get_opponents(self, name):
        return [p for n, p in self.players.items() if n != name]

    def log_action(self, message):
        self.log.append(message)
        print(f"[LOG] {message}")

    def load_from_json(self, json_data, card_library):
        for player_name, pdata in json_data["players"].items():
            from core.player_state import PlayerState
            ps = PlayerState(player_name)

            ps.life = pdata.get("life", 40)

            for zone_name in ["hand", "battlefield", "library", "graveyard"]:
                cards = pdata.get(zone_name, [])
                setattr(ps, zone_name, [card_library[c] for c in cards])

            self.add_player(ps)
