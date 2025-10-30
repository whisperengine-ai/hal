import core.mana_utils as mana_utils

# core/game_actions.py

class GameActions:
    def __init__(self, game_state, rule_state, log_manager):
        self.game_state = game_state
        self.rule_state = rule_state
        self.log_manager = log_manager
            
    def perform_draw(self, player, trigger_manager=None):
        if player.library:
            card = player.library.pop(0)
            player.hand.append(card)
            self.log_manager.log_action(player, f"draws {card.name}.")

            if trigger_manager:
                # EXAMPLE: check for draw-based triggers
                # trigger_manager.check_and_trigger("card_drawn", card=card, player=player)
                pass

            return card
        else:
            self.log_manager.log_action(player, "tries to draw, but library is empty.")
            return None

    def play_land(self, player, card):
        if card.card_type != "Land":
            self.log_manager.log_action(f"❌ {card.name} is not a land.")
            return

        if player.lands_played_this_turn >= 1:
            self.log_manager.log_action(f"❌ {player.name} has already played a land this turn.")
            return

        if card not in player.hand:
            self.log_manager.log_action(f"❌ {card.name} is not in {player.name}'s hand.")
            return

        player.hand.remove(card)
        player.battlefield.append(card)
        player.lands_played_this_turn += 1
        self.log_manager.log_action(f"🌿 {player.name} plays land: {card.name}")

    def perform_main_phase_actions(self, player):
        """Perform main phase actions for the given player."""
        player.ai.attempted_casts_this_phase.clear()  # Only clear PHASE memory

        for card in player.hand:
            if card.name in player.ai.attempted_casts_this_phase:
                continue  # Already tried this card this phase — don't spam it

            if not player.ai.can_pay_mana_cost(card):
                player.ai.attempted_casts_this_phase.add(card.name)
                player.ai.attempted_casts_this_turn.add(card.name)  # Long term memory
                self.log_manager.log_action(
                    f"{player.name} cannot pay for {card.name} — skipping."
                )
                continue

            # If we reach here, we CAN cast:
            self.cast_spell(player, card)
            player.ai.attempted_casts_this_phase.add(card.name)
            player.ai.attempted_casts_this_turn.add(card.name)
            self.log_manager.log_action(
                f"{player.name} successfully casts {card.name}!"
            )

    def log_action(self, message):
        self.log_manager.log_action(message)


    def add_mana_to_pool(self, color, amount=1):
        self.rule_state.mana_pool[color] += amount
        self.log_manager.log_action(f"{self.rule_state.current_player.name}: added {amount} {color} mana to mana pool")

    def clear_mana_pool(self):
        for color in self.rule_state.mana_pool:
            self.rule_state.mana_pool[color] = 0
        self.log_manager.log_action("Mana pool cleared")

    def can_pay_mana_cost(self, player_state, mana_cost_str):
        parsed_cost = mana_utils.parse_mana_cost(mana_cost_str)
        print(f"DEBUG: Parsed mana cost: {parsed_cost}")
        available_mana = player_state.get_available_mana(self.game_state.battlefield)
        return mana_utils.can_pay_mana_cost(available_mana, mana_cost_str)
    
    def cast_nonland_permanent(self, player_state, game_state, card):
        # Attempt to pay mana cost
        if mana_utils.pay_mana_cost(player_state, game_state, card.mana_cost):
            self.log_manager.log_action(f"{player_state.name} casts {card.name}!")
            
            # Move card from hand → battlefield
            player_state.hand.remove(card)
            game_state.battlefield.append(card)
            self.game_state.trigger_manager.check_and_trigger("enters_battlefield", card=card, player=player_state) #CHECK TRIGGERS

            
            # Log battlefield update
            self.log_manager.log_action(f"{card.name} enters the battlefield under {player_state.name}'s control.")
        else:
            self.log_manager.log_action(f"{player_state.name} failed to pay for {card.name}.")
            return  # Do not move card if payment failed!
            

    def get_available_mana(self, battlefield):
            untapped_lands = [
                card for card in battlefield
                if card.controller == self.name and card.card_type == "Land" and not card.is_tapped
            ]
            return len(untapped_lands)