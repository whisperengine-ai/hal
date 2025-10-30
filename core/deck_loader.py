from card_actions.card_lookup import card_lookup
import re

def normalize_card_name(name):
    return name.replace(",", "").replace("'", "").title()

class DeckLoader:
    def __init__(self, deck_path):
        print("DEBUG: DeckLoader __init__ starting")
        self.deck_path = deck_path
        self.deck_list = []
        self.mainboard = []
        print("DEBUG: DeckLoader __init__ Ended")

    def load(self):
        try:
            self.deck_list = []
            seen = set()

            # Basics + snow-covered versions (exempt from singleton rules)
            basics = {
                "Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes",
                "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp",
                "Snow-Covered Mountain", "Snow-Covered Forest"
            }

            with open(self.deck_path, 'r', encoding='utf-8') as file:
                for raw in file:
                    line = raw.strip()
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue

                    # Handle SB: prefix (sideboard lines)
                    if line.lower().startswith('sb:'):
                        line = line[3:].strip()
                        if not line:
                            continue

                    # Match "1 Card", "1x Card", etc.
                    m = re.match(r'^(\d+)[xX]?\s+(.+)$', line)
                    if m:
                        qty = int(m.group(1))
                        card_name = m.group(2)
                    else:
                        qty = 1
                        card_name = line

                    # Singleton enforcement (skip duplicates unless it's a basic)
                    if card_name in seen and card_name not in basics:
                        print(f"🚫 Duplicate card ignored (singleton): '{card_name}'")
                        continue

                    seen.add(card_name)
                    # Add quantity copies (for basics, quantity may be > 1)
                    self.deck_list.extend([card_name] * qty)

            # Build card objects
            self.mainboard = []
            for card_name in self.deck_list:
                key = normalize_card_name(card_name)
                if key in card_lookup:
                    self.mainboard.append(card_lookup[key])
                else:
                    print(f"⚠️ Card '{card_name}' not found in card_lookup.")

            print(f"📥 Loaded singleton deck from {self.deck_path} with {len(self.mainboard)} card objects.")
            print(f"CraigAI library size at start of game: {len(self.mainboard)}")

        except FileNotFoundError:
            print(f"❌ Deck file not found: {self.deck_path}")
        except Exception as e:
            print(f"❌ Error while loading deck '{self.deck_path}': {e}")



    def get_commander(self):
        return self.commander

    def get_mainboard(self):
        return self.mainboard