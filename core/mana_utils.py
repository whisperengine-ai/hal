import re


def parse_mana_cost(mana_cost_str):
    """
    Parses a mana cost string like '{1}{G}{G}' into a list of symbols: ['1', 'G', 'G'].
    Handles generic mana, colored mana, hybrid mana, Phyrexian mana, variable costs, etc.
    """
    return re.findall(r"\{(.*?)\}", mana_cost_str)

def can_pay_mana_cost(available_mana, mana_cost):
    parsed_cost = parse_mana_cost(mana_cost)
    print(f"DEBUG: Parsed mana cost: {parsed_cost}")
    total_required = len(parsed_cost)
    return available_mana >= total_required

def pay_mana_cost(player_state, game_state, mana_cost):
    parsed_cost = parse_mana_cost(mana_cost)
    print(f"DEBUG: Paying mana cost: {parsed_cost}")

    battlefield = game_state.battlefield

    # Find untapped lands controlled by player
    available_lands = [
        card for card in battlefield
        if card.controller == player_state.name and card.card_type == "Land" and not card.is_tapped
    ]

    for symbol in parsed_cost:
        if not available_lands:
            print(f"WARNING: Not enough lands to pay for symbol '{symbol}'!")
            return False  # Cannot pay full cost

        # Pop a land to tap
        land = available_lands.pop(0)
        land.is_tapped = True
        print(f"{player_state.name} taps {land.name} to pay for '{symbol}'.")

        # Optionally, you can add to the mana pool here:
        # game_manager.game_actions.add_mana_to_pool(...)

    return True