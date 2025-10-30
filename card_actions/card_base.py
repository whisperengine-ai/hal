

class Card:
    def __init__(self, name):
        self.name = name
        self.card_type = "Unknown"
        self.mana_cost = None
        self.rules_text = ""
        self.abilities = []
        self.subtypes = []

class SplitCard(Card):
    def __init__(self, name, left_name, right_name, left_type, right_type):
        super().__init__(name)
        self.card_type = "Split"
        self.left_name = left_name
        self.right_name = right_name
        self.left_type = left_type
        self.right_type = right_type
        self.subtypes = ["Split"]

class CreatureCard(Card):
    def __init__(self, name, power=0, toughness=0):
        super().__init__(name)
        self.card_type = "Creature"
        self.power = power
        self.toughness = toughness

class LandCard(Card):
    def __init__(self, name):
        super().__init__(name)
        self.card_type = "Land"

class EnchantmentCard(Card):
    def __init__(self, name):
        super().__init__(name)
        self.card_type = "Enchantment"

class InstantCard(Card):
    def __init__(self, name):
        super().__init__(name)
        self.card_type = "Instant"

class SorceryCard(Card):
    def __init__(self, name):
        super().__init__(name)
        self.card_type = "Sorcery"

class ArtifactCard(Card):
    def __init__(self, name):
        super().__init__(name)
        self.card_type = "Artifact"

class EquipmentCard(ArtifactCard):
    def __init__(self, name, equip_cost):
        super().__init__(name)
        self.subtypes.append("Equipment")
        self.equip_cost = equip_cost

class ArtifactCreatureCard(CreatureCard):
    def __init__(self, name, power=0, toughness=0):
        super().__init__(name, power, toughness)
        self.card_type = "Artifact Creature"
        self.subtypes.append("Artifact")
        self.subtypes.append("Creature")

class EnchantmentCreatureCard(CreatureCard):
    def __init__(self, name, power=0, toughness=0):
        super().__init__(name, power, toughness)
        self.card_type = "Enchantment Creature"
        self.subtypes.append("Enchantment")
        self.subtypes.append("Creature")

class ArtifactEquipmentCreatureCard(CreatureCard):
    def __init__(self, name, power=0, toughness=0, reconfigure_cost=None):
        super().__init__(name, power, toughness)
        self.card_type = "Artifact Creature"
        self.subtypes.append("Artifact")
        self.subtypes.append("Creature")
        self.subtypes.append("Equipment")
        self.equip_cost = reconfigure_cost
        self.is_equipped = False

    def __str__(self):
        # Safe string representation — no crash if game_manager is not patched yet
        if self.game_manager is None or self.game_manager.game_state is None:
            return f"{self.name} ({self.card_type})"
        else:
            # Later → you can add more complex logic if needed
            return f"{self.name} ({self.card_type})"
        
    def __repr__(self):
        return f"<Card: {self.name}>"
 