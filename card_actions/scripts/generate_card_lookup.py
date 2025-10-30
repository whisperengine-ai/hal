import ast

CARD_BASE_PATH = 'card_actions/card_base.py'

def extract_card_instances(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source)

    card_names = []
    for node in tree.body:
        # Looking for assignments of Card instances like: var_name = Card(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if getattr(node.value.func, 'id', '') == 'Card':
                # The variable name assigned is node.targets[0].id
                card_var = node.targets[0].id
                card_names.append(card_var)
    return card_names

def generate_lookup_dict(card_vars):
    lines = []
    lines.append("from card_actions.card_base import *\n")
    lines.append("card_lookup = {\n")
    for var in card_vars:
        # We try to guess the card name string from var name for demo, 
        # but best to just use original card names manually for precision.
        # Here we do a simple transform for example:
        card_name = var.replace("_", " ").title()
        lines.append(f'    "{card_name}": {var},\n')
    lines.append("}\n")
    return ''.join(lines)

if __name__ == "__main__":
    card_vars = extract_card_instances(CARD_BASE_PATH)
    lookup_code = generate_lookup_dict(card_vars)
    with open('card_actions/card_lookup.py', 'w', encoding='utf-8') as f:
        f.write(lookup_code)
    print(f"Generated card_lookup with {len(card_vars)} entries.")