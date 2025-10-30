import os
import re
import requests

# Adjust this import path to your project structure
CARD_BASE_IMPORT = "from card_actions.card_base import Card\n\n"

def sanitize_mana_cost(mana_cost):
    if not mana_cost:
        return ""
    s = mana_cost.replace('""', '"')
    s = re.sub(r'"\{(\w+)\}"', r'{\1}', s)
    s = s.replace('"', '')
    return s

def sanitize_text(text):
    if not text:
        return '""'
    text = text.replace('"""', '\\"\\"\\"')
    return f'"""{text}"""'

def fetch_card_data(card_name):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Warning: Could not fetch data for '{card_name}'")
        return None
    data = resp.json()
    return {
        "mana_cost": data.get("mana_cost", ""),
        "type_line": data.get("type_line", ""),
        "oracle_text": data.get("oracle_text", ""),
        "colors": data.get("colors", []),
        "cmc": data.get("cmc", 0)
    }

def parse_decklist(deck_text):
    card_names = []
    lines = deck_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.lower() in ["commander", "deck", "sideboard"]:
            continue
        match = re.match(r'(\d+)\s+(.*)', line)
        if match:
            name = match.group(2).strip()
            card_names.append(name)
        else:
            card_names.append(line)
    return card_names

def sanitize_var_name(card_name):
    return re.sub(r"[^a-z0-9_]", "", card_name.lower().replace(" ", "_"))

def generate_cards_file(deck_file_path, output_file_path):
    with open(deck_file_path, "r", encoding="utf-8") as f:
        deck_text = f.read()

    card_names = parse_decklist(deck_text)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(CARD_BASE_IMPORT)
        for card_name in card_names:
            card_data = fetch_card_data(card_name)
            if not card_data:
                continue

            var_name = sanitize_var_name(card_name)
            mana_cost = sanitize_mana_cost(card_data["mana_cost"])
            card_type = card_data["type_line"].replace('"', '\\"')
            oracle_text = sanitize_text(card_data["oracle_text"])
            colors = card_data["colors"]
            cmc = card_data["cmc"]
            color_id = "[" + ", ".join(f'"{c}"' for c in colors) + "]" if colors else "[]"
            mana_produced = "[]"  # Optional: fill later if desired

            f.write(f"{var_name} = Card(\n")
            f.write(f'    name="{card_name}",\n')
            f.write(f'    mana_cost="{mana_cost}",\n')
            f.write(f'    card_type="{card_type}",\n')
            f.write(f'    subtype="",\n')
            f.write(f'    supertype="",\n')
            f.write(f'    mana_produced={mana_produced},\n')
            f.write(f'    color_id={color_id},\n')
            f.write(f'    text={oracle_text},\n')
            f.write(f'    own_by="player",\n')
            f.write(f'    control_by="player",\n')
            f.write(f'    mana_value={cmc}\n')
            f.write(")\n\n")

    print(f"Generated {output_file_path} for {len(card_names)} cards.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    deck_file = os.path.join(script_dir, "combined_deck.txt")
    output_file = os.path.join(script_dir, "generated_cards.py")
    generate_cards_file(deck_file, output_file)