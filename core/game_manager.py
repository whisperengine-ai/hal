
from core.trigger_manager import TriggerManager
from core.game_state import GameState
from core.stack_manager import StackManager
from core.rule_state import RuleState
from core.game_state import GameState
from core.player_state import PlayerState
from core.game_actions import GameActions
from config import OFFLINE_DEMO_MODE
from ai.craig import Craig


class GameManager:
    def __init__(self, players, rule_state_class, log_manager_class, game_state_class, trigger_manager, stack_manager_class,):
        print("DEBUG: GameManager __init__ started")

        print(f"DEBUG: Players passed to GameManager: {[p.name for p in players]}")
        self.players = players
        print(f"DEBUG: manual_control flags: {[p.manual_control for p in self.players]}")

        # Create GameState first
        self.game_state = game_state_class(self)
        print("DEBUG: GameManager self.game_state assigned")

        # Create LogManager
        self.log_manager = log_manager_class("game_log.txt")
        print("DEBUG:LOG MANAGER ASSIGNED")

        # Create GameActions with placeholder RuleState (None for now)
        self.game_actions = GameActions(self.game_state, None, self.log_manager)
        print("DEBUG: GameManager game_actions assigned")

        # Now create RuleState with correct GameActions and GameState
        self.rule_state = rule_state_class(self.game_state, self.game_actions, self)
        print("DEBUG: GameManager rule_state assigned")

        # Patch GameActions with the correct RuleState
        self.game_actions.rule_state = self.rule_state
        print("DEBUG: GameManager game_actions.rule_state patched")

        # Create TriggerManager
        self.trigger_manager = trigger_manager(self)
        print("DEBUG: TRIGGER MANAGER ASSIGNED")

        # Create StackManager
        self.stack_manager = stack_manager_class(self)
        print("DEBUG: GameManager stack_manager assigned")

        # Optional → link TriggerManager to other systems
        self.rule_state.trigger_manager = self.trigger_manager
        self.game_state.trigger_manager = self.trigger_manager  # MVP link

        # Init other fields
        self.current_player_index = 0
        self.turn_number = 1
        self.card_engine = None  # This can be set externally if needed

        self.current_game_state = None
        self.game_running = True
        self.priority_passed = False
        self.holding_priority = False

        print("card detection engine assigned")
        print("DEBUG: GameManager __init__ completed")

       

    def move_to_battlefield(self, card, player_name):
        player = next(p for p in self.players if p.name == player_name)

        if card.card_type.lower() == "land":
            card.controller = player.name
            card.owner = player.name
            self.game_actions.play_land(player, card, self.trigger_manager)
        else:
            self.game_state.battlefield.append(card)
            card.controller = player.name
            card.owner = player.name
            self.log_manager.log_action(f"✅ {player_name} moves {card.name} to battlefield.")

    def start_game(self):
        print("🎮 Starting the game...")
        self.rule_state.phase = "begin"
        for player in self.players:
            for _ in range(7):
                print(f"DEBUG: {player.name} hand at start of game: {[card.name for card in player.hand]}")
                if player.library:
                    card = player.library.pop(0)
                    player.hand.append(card)
            
            print(f"DEBUG: {player.name} ai={player.ai} manual_control={player.manual_control}")
            if not player.manual_control and player.ai:
                player.ai.game_state = self
                player.ai.take_turn()      
        self.execute_turn()

    def execute_turn(self):
        player = self.players[self.current_player_index]
        print(f"➡️ Turn {self.turn_number}: {player.name}'s turn begins")
        
        # Print battlefield state at start of turn
        self.print_shared_battlefield()

        # Advance phases and allow AI to act
        self.rule_state.phase = "draw"
        if not player.manual_control and player.ai:
            player.ai.take_turn()

        # Print battlefield state before ending turn
        print(f"🔄 End of {player.name}'s turn — final battlefield state:")
        self.print_shared_battlefield()

    def run_game(self):
        print("🎮 Starting game loop...")
        self.turn_number = 1
        self.current_player_index = 0

        while self.game_running:
            print(f"[DEBUG] Game loop - current_game_state = {type(self.current_game_state).__name__ if self.current_game_state else 'None'}")
            if self.current_game_state:
                self.current_game_state.update()
            else:
                self.execute_turn()

        print("🏁 Game over.")
   

    def check_game_end(self):
        # Placeholder for win/loss logic
        for player in self.players:
            if player.life <= 0:
                print(f"☠️ {player.name} has lost the game!")

    def print_shared_battlefield(self):
        print("\n=== Shared Battlefield ===")
        if not self.game_state.battlefield:
            print("(Empty)")
        else:
            for card in self.game_state.battlefield:
                print(f"  - {card.name} ({card.card_type}) controlled by {card.controller}")
        print("========================\n")

    def draw_card(self, player_state):
        if player_state.library:
            card = player_state.library.pop(0)
            player_state.hand.append(card)
            self.log_manager.log_action(f"{player_state.name} draws: {card.name}")
        else:
            self.log_manager.log_action(f"{player_state.name} has no cards left to draw!")

    def cast_spell(self, card, player_name):
        self.log_manager.log_action(f"{player_name} attempts to cast {card.name}")
        current_game_state = PriorityPhaseState(self)

        self.stack_manager.add_to_stack(
            type='spell',
            source_card=card,
            controller=player_name,
            targets=[],
            metadata={}
        )

        # Now run the proper stack loop
        from core.priority_phase_state import PriorityPhaseState
        self.current_game_state = PriorityPhaseState(self)

    def apply(self, action):
        print(f"[GameManager] Applying action: {action}")

        if action["type"] == "noop":
            print("[GameManager] No operation.")
        
        elif action["type"] == "draw":
            player = self.players[self.current_player_index]
            self.draw_card(player)

        elif action["type"] == "end_turn":
            self.advance_to_next_player()

        else:
            print(f"[GameManager] Unknown action: {action}")

    def add_player(self, player):
        self.players[player.name] = player
        if len(self.players) == 1:
            self.active_player = player.name  # or player object
        print(f"👤 Added player: {player.name}")

    def get_game_state(self):
        return self.game_state
    
def run(self):
    self.current_turn_index = 0
    self.turn_order = list(self.players.values())

    while True:  # for now, infinite loop until button-controlled
        active_player = self.turn_order[self.current_turn_index]
        self.log_manager.log_action(f"\n🔄 Turn: {active_player.name}")

        if not active_player.manual_control:
            # eventually call: craig.take_turn()
            self.ai_play_turn(active_player)
        else:
            self.prompt_gui_for_player_turn(active_player)

        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

