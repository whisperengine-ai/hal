class PlayerState:
    def __init__(self, name, manual_control=True,):
        print("DEBUG: PlaterState __init__ starting")
        self.name = name
        self.life = 40
        self.hand = []
        self.library = []
        self.graveyard = []
        self.exile = []
        self.command_zone = []
        self.untapped_land = []
        self.untapped_creature = []
        self.untapped_artifact = []
        self.instants_can_cast = []
        self.sorceries_can_cast = []
        self.can_attack = []
        self.can_block = []
        self.manual_control = manual_control
        self.ai = None
        self.mana_pool = {
        "W": 0,  # White
        "U": 0,  # Blue
        "B": 0,  # Black
        "R": 0,  # Red
        "G": 0,  # Green
        "C": 0   # Colorless (if needed)
}
        print("DEBUG: PlaterState __init__ complete")

    def get_available_mana(self, battlefield):
        untapped_lands = [
            card for card in battlefield
            if card.controller == self.name and card.card_type == "Land" and not card.is_tapped
        ]
        return len(untapped_lands)

    def __repr__(self):
        zone_size = len(self.hand) if hasattr(self, "hand") else 0
        return f"<PlayerState: {self.name}, Hand: {zone_size}>"
    

    def draw_hand(self, count=7):
        for _ in range(count):
            if self.library:
                self.hand.append(self.library.pop(0))
            else:
                print(f"⚠️ {self.name} tried to draw from an empty library!")