

class StackManager:
    def __init__(self, game_manager,):
        self.stack = []
        self.game_manager = game_manager
        print("DEBUG: StackManager created → game_manager is:", "Assigned" if game_manager else "None")

    def add_to_stack(self, type, source_card, controller, targets=[], metadata={}):
        print(f"🌀 Stack: Adding {type} → {source_card.name} controlled by {controller}")
        self.stack.append({
            "type": type,
            "source_card": source_card,
            "controller": controller,
            "targets": targets,
            "metadata": metadata
        })
        self.print_stack()

    def print_stack(self):
        if not self.stack:
            print("🌀 Stack is empty.")
        else:
            print("🌀 Current Stack (top first):")
            for item in reversed(self.stack):
                print(f"  - {item['type']} → {item['source_card'].name} controlled by {item['controller']}")

    def pop_stack(self):
        if self.stack:
            item = self.stack.pop()
            print(f"🌀 Resolving {item['type']} → {item['source_card'].name} controlled by {item['controller']}")
            return item
        else:
            print("🌀 Stack is empty — nothing to resolve.")
            return None

    # Method to pass priority to players (basic prototype — later this will be more advanced)
    def pass_priority(self, players, current_priority_index):
        num_players = len(players)
        passes_in_a_row = 0

        i = current_priority_index

        while passes_in_a_row < num_players:
            player = players[i]
            self.print_stack()

            response = input(f"{player.name}, respond to the stack (type card name or 'pass'): ").strip()

            if response.lower() == "pass":
                print(f"✅ {player.name} passes priority.")
                passes_in_a_row += 1
                i = (i + 1) % num_players  # Next player in turn order

            else:
                # Attempt to look up card
                if response in self.game_manager.card_lookup:
                    card_to_cast = self.game_manager.card_lookup[response]

                    # Add to stack using the EXISTING add_to_stack() method
                    self.add_to_stack(type="spell", source_card=card_to_cast, controller=player.name)
                    print(f"🛑 {player.name} responds with {card_to_cast.name} → added to stack.")

                    # After adding to stack → priority restarts
                    return False, i
                else:
                    print(f"⚠️ Unknown card: '{response}'. Please try again.")
                    # Let them retry — do not advance to next player

        # If all players passed → ready to resolve
        return True, i
    
    def is_empty(self):
        return len(self.stack) == 0
