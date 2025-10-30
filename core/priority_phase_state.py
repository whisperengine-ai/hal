from core.phase_state import PhaseState

class PriorityPhaseState(PhaseState):
    def __init__(self, game_manager):
        super().__init__(self, game_manager)
        self.current_priority_index = 0
        print("[DEBUG] Entering Priority Phase")

    def update(self):
        players = self.game_manager.players
        player = players[self.current_priority_index]

        print(f"[DEBUG] Current Priority Player: {player.name} (index {self.current_priority_index})")

    # AI player auto-passes
        if not player.manual_control and player.ai:
            print(f"[DEBUG] {player.name} (AI) auto-passes priority.")
            self.game_manager.priority_passed = True
            self.game_manager.holding_priority = False

        # Human player → UI will control flags

        # Process pass priority logic
        if self.game_manager.priority_passed:
            print(f"[DEBUG] {player.name} passed priority.")
            self.game_manager.priority_passed = False
            self.current_priority_index = (self.current_priority_index + 1) % len(players)

            if self.current_priority_index == 0:
                if not self.game_manager.stack_manager.is_empty():
                    print("[DEBUG] All players passed — resolving top stack item.")
                    self.game_manager.stack_manager.resolve_top_item()
                else:
                    print("[DEBUG] Stack empty — exiting Priority Phase.")
                    self.game_manager.current_game_state = None
        elif self.game_manager.holding_priority:
            print(f"[DEBUG] {player.name} is holding priority — waiting.")