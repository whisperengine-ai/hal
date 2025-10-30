# log_manager.py

import os
import datetime

class LogManager:
    def __init__(self, filepath="game_log.txt"):
        self.filepath = filepath

        # Ensure the folder exists
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)

        with open(self.filepath, "w") as f:
            print("log created!")
            f.write("=== Game Log Started ===\n")

    def _write_log(self, message):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}"
        print(full_message)  # Console output
       
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")

    def log_action(self, message):
        print(message)
        self._write_log(message)

    def log_trigger(self, trigger_type, source):
        self._write_log(f"Triggered Ability ({trigger_type}) from {source}")

    def log_combat(self, attacker, target):
        self._write_log(f"Combat: {attacker} attacks {target.name}")

    def log_stack_addition(self, effect, source, controller):
        self._write_log(f"Stack: {source} ({effect}) added by {controller.name}")

    def log_phase(self, phase_name):
        self._write_log(f"Phase: {phase_name}")

if __name__ == "__main__":
    from core.player_state import PlayerState
    logger = LogManager()
    test_player = PlayerState("Brad")
    logger.log_action(test_player, "played Temple Garden")
    logger.log_trigger("landfall", "Felidar Retreat")
    logger.log_combat("Goblin Guide", test_player)
    logger.log_stack_addition("Lightning Bolt", "Lightning Bolt", test_player)
    logger.log_phase("Main Phase 1")