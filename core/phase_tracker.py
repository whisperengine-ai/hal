# phase_tracker.py

from core.rule_state import RuleState

class PhaseTracker:
    def __init__(self, rule_state):
        self.rule_state = rule_state

    def start_turn(self, player_name):
        self.rule_state.active_player = player_name
        self.rule_state.current_phase = "beginning"
        print(f"\n🔁 New turn begins for {player_name}! Starting at {self.rule_state.current_phase} phase.")

    def next_phase(self):
        current = self.rule_state.current_phase
        self.rule_state.advance_phase()
        new = self.rule_state.current_phase
        print(f"➡️ Phase advanced: {current} ➡️ {new}")

    def run_turn(self, player_name):
        self.start_turn(player_name)
        for _ in range(len(self.rule_state.phase_order)):
            self.next_phase()
            # 🔍 Insert future logic for casting, triggers, etc. here

if __name__ == "__main__":
    rs = RuleState()
    tracker = PhaseTracker(rs)
    tracker.run_turn("Brad")
    rs.print_current_state()