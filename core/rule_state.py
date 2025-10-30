# rule_state.py

class RuleState:
    def __init__(self, game_state, game_actions, game_manager):
        print("DEBUG: RuleState __init__ starting")
        self.game_state = game_state
        self.game_actions = game_actions 
        # Turn structure rules
        self.phase = "beginning"
        self.current_phase = "beginning"
        self.phase_order = [
            "beginning",
            "untap",
            "upkeep",
            "draw",
            "main1",
            "combat",
            "main2",
            "end",
        ]
        print("DEBUG: RuleState __init__ complete")

        # Priority rules
        self.priority_passed = False
        self.active_player = None
        self.current_priority_player = None

        # Casting permissions
        self.rules = {
            "can_cast_sorceries_during_combat": False,
            "can_cast_instant_from_graveyard": False,
            "can_cast_creature_as_instant": False,
            "may_skip_upkeep": False,
            "draw_extra_card": 0,
            "skip_draw_step": False,
            "max_hand_size": 7,
            "can_cast_from_exile": False,
            "players_cannot_gain_life": False
        }

        # Active continuous effects from cards
        self.continuous_effects = []

        # Player Mana Pools
        self.mana_pool = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}

    def advance_phase(self):
        try:
            current_index = self.phase_order.index(self.current_phase)
            self.current_phase = self.phase_order[(current_index + 1) % len(self.phase_order)]
            print(f"✅ Phase advanced to: {self.current_phase}")
        except ValueError:
            print(f"⚠️ Phase error: '{self.current_phase}' not found in phase_order.")

    def apply_effect(self, rule_key, value):
        if rule_key in self.rules:
            self.rules[rule_key] = value
        else:
            print(f"⚠️ Rule key '{rule_key}' not found. Consider adding it to the engine.")

    def add_continuous_effect(self, description):
        self.continuous_effects.append(description)

    def clear_all_effects(self):
        self.rules = {key: False if isinstance(value, bool) else 0 for key, value in self.rules.items()}
        self.continuous_effects.clear()

    def print_current_state(self):
        print("\n📜 Current Rule State:")
        print(f"Phase: {self.current_phase}")
        for rule, value in self.rules.items():
            print(f" - {rule}: {value}")
        if self.continuous_effects:
            print("Active continuous effects:")
            for effect in self.continuous_effects:
                print(f" * {effect}")
        else:
            print("No continuous effects.")


    