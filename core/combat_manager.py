# combat_manager.py

class CombatManager:
    def __init__(self, rule_state, stack_manager):
        print("DEBUG: CombatManager __init__ starting")
        self.rule_state = rule_state
        self.stack_manager = stack_manager
        self.combat_log = []
        print("DEBUG: CombatManager __init__ starting")

    def declare_attackers(self, player, targets):
        """
        Declare attackers. 'targets' is a list of (attacker, defending_player) tuples.
        """
        if not self.rule_state.phase == "Combat":
            print("❌ Not the combat phase.")
            return

        print(f"⚔️ {player.name} declares attackers:")
        for attacker, target in targets:
            print(f"- {attacker} attacking {target.name}")
            self.combat_log.append((attacker, target))

    def declare_blockers(self, defender, blocks):
        """
        Declare blockers. 'blocks' is a list of (blocker, attacker) tuples.
        """
        print(f"🛡️ {defender.name} declares blockers:")
        for blocker, attacker in blocks:
            print(f"- {blocker} blocks {attacker}")
            self.combat_log.append((blocker, attacker))

    def resolve_combat(self):
        print("💥 Resolving combat damage...")
        for entry in self.combat_log:
            print(f"- {entry[0]} deals damage to {entry[1].name if hasattr(entry[1], 'name') else entry[1]}")
        self.combat_log.clear()


