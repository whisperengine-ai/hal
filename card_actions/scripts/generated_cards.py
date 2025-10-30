from card_actions.card_base import *

access_tunnel = Card(
    name="Access Tunnel",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add {C}.
{3}, {T}: Target creature with power 3 or less can't be blocked this turn.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

alms_collector = Card(
    name="Alms Collector",
    mana_cost="{3}{W}",
    card_type="Creature — Cat Cleric",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flash
If an opponent would draw two or more cards, instead you and that player each draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

anguished_unmaking = Card(
    name="Anguished Unmaking",
    mana_cost="{1}{W}{B}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "W"],
    text="""Exile target nonland permanent. You lose 3 life.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

animal_sanctuary = Card(
    name="Animal Sanctuary",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add {C}.
{2}, {T}: Put a +1/+1 counter on target Bird, Cat, Dog, Goat, Ox, or Snake.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

anointed_procession = Card(
    name="Anointed Procession",
    mana_cost="{3}{W}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""If an effect would create one or more tokens under your control, it creates twice that many of those tokens instead.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

arasta_of_the_endless_web = Card(
    name="Arasta of the Endless Web",
    mana_cost="{2}{G}{G}",
    card_type="Legendary Enchantment Creature — Spider",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Reach
Whenever an opponent casts an instant or sorcery spell, create a 1/2 green Spider creature token with reach.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

arbor_adherent = Card(
    name="Arbor Adherent",
    mana_cost="{3}{G}",
    card_type="Creature — Dog Druid",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""{T}: Add one mana of any color.
{T}: Add X mana of any one color, where X is the greatest toughness among other creatures you control.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

arboreal_grazer = Card(
    name="Arboreal Grazer",
    mana_cost="{G}",
    card_type="Creature — Sloth Beast",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Reach
When this creature enters, you may put a land card from your hand onto the battlefield tapped.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

arcane_signet = Card(
    name="Arcane Signet",
    mana_cost="{2}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add one mana of any color in your commander's color identity.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

assault_formation = Card(
    name="Assault Formation",
    mana_cost="{1}{G}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Each creature you control assigns combat damage equal to its toughness rather than its power.
{G}: Target creature with defender can attack this turn as though it didn't have defender.
{2}{G}: Creatures you control get +0/+1 until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

axebane_guardian = Card(
    name="Axebane Guardian",
    mana_cost="{2}{G}",
    card_type="Creature — Human Druid",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
{T}: Add X mana in any combination of colors, where X is the number of creatures you control with defender.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

baldin_century_herdmaster = Card(
    name="Baldin, Century Herdmaster",
    mana_cost="{4}{W}{W}",
    card_type="Legendary Creature — Human Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""During your turn, each creature assigns combat damage equal to its toughness rather than its power.
Whenever Baldin attacks, up to one hundred target creatures each get +0/+X until end of turn, where X is the number of cards in your hand.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

basilisk_collar = Card(
    name="Basilisk Collar",
    mana_cost="{1}",
    card_type="Artifact — Equipment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Equipped creature has deathtouch and lifelink. (Any amount of damage it deals to a creature is enough to destroy it. Damage dealt by this creature also causes you to gain that much life.)
Equip {2} ({2}: Attach to target creature you control. Equip only as a sorcery.)""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

beastmaster_ascension = Card(
    name="Beastmaster Ascension",
    mana_cost="{2}{G}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Whenever a creature you control attacks, you may put a quest counter on this enchantment.
As long as this enchantment has seven or more quest counters on it, creatures you control get +5/+5.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

behind_the_scenes = Card(
    name="Behind the Scenes",
    mana_cost="{2}{B}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Creatures you control have skulk. (They can't be blocked by creatures with greater power.)
{4}{W}: Creatures you control get +1/+1 until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

betor_ancestors_voice = Card(
    name="Betor, Ancestor's Voice",
    mana_cost="{2}{W}{B}{G}",
    card_type="Legendary Creature — Spirit Dragon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "G", "W"],
    text="""Flying, lifelink
At the beginning of your end step, put a number of +1/+1 counters on up to one other target creature you control equal to the amount of life you gained this turn. Return up to one target creature card with mana value less than or equal to the amount of life you lost this turn from your graveyard to the battlefield.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

blight_pile = Card(
    name="Blight Pile",
    mana_cost="{1}{B}",
    card_type="Creature — Phyrexian",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Defender
{2}{B}, {T}: Each opponent loses X life, where X is the number of creatures with defender you control.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

bloodline_pretender = Card(
    name="Bloodline Pretender",
    mana_cost="{3}",
    card_type="Artifact Creature — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Changeling (This card is every creature type.)
As this creature enters, choose a creature type.
Whenever another creature you control of the chosen type enters, put a +1/+1 counter on this creature.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

bojuka_bog = Card(
    name="Bojuka Bog",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
When this land enters, exile target player's graveyard.
{T}: Add {B}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

brimaz_king_of_oreskos = Card(
    name="Brimaz, King of Oreskos",
    mana_cost="{1}{W}{W}",
    card_type="Legendary Creature — Cat Soldier",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Vigilance
Whenever Brimaz attacks, create a 1/1 white Cat Soldier creature token with vigilance that's attacking.
Whenever Brimaz blocks a creature, create a 1/1 white Cat Soldier creature token with vigilance that's blocking that creature.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

canopy_gargantuan = Card(
    name="Canopy Gargantuan",
    mana_cost="{5}{G}{G}",
    card_type="Creature — Dragon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Flying, ward {2}
At the beginning of your upkeep, put a number of +1/+1 counters on each other creature you control equal to that creature's toughness.""",
    own_by="player",
    control_by="player",
    mana_value=7.0
)

canopy_vista = Card(
    name="Canopy Vista",
    mana_cost="",
    card_type="Land — Forest Plains",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {G} or {W}.)
This land enters tapped unless you control two or more basic lands.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

carven_caryatid = Card(
    name="Carven Caryatid",
    mana_cost="{1}{G}{G}",
    card_type="Creature — Spirit",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender (This creature can't attack.)
When this creature enters, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

cast_out = Card(
    name="Cast Out",
    mana_cost="{3}{W}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flash
When this enchantment enters, exile target nonland permanent an opponent controls until this enchantment leaves the battlefield.
Cycling {W} ({W}, Discard this card: Draw a card.)""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

cinder_glade = Card(
    name="Cinder Glade",
    mana_cost="",
    card_type="Land — Mountain Forest",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {R} or {G}.)
This land enters tapped unless you control two or more basic lands.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

clifftop_retreat = Card(
    name="Clifftop Retreat",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control a Mountain or a Plains.
{T}: Add {R} or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

colfenors_urn = Card(
    name="Colfenor's Urn",
    mana_cost="{3}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Whenever a creature with toughness 4 or greater is put into your graveyard from the battlefield, you may exile it.
At the beginning of the end step, if three or more cards have been exiled with this artifact, sacrifice it. If you do, return those cards to the battlefield under their owner's control.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

command_tower = Card(
    name="Command Tower",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add one mana of any color in your commander's color identity.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

crashing_drawbridge = Card(
    name="Crashing Drawbridge",
    mana_cost="{2}",
    card_type="Artifact Creature — Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Defender
{T}: Creatures you control gain haste until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

crib_swap = Card(
    name="Crib Swap",
    mana_cost="{2}{W}",
    card_type="Kindred Instant — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Changeling (This card is every creature type.)
Exile target creature. Its controller creates a 1/1 colorless Shapeshifter creature token with changeling.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

cultivate = Card(
    name="Cultivate",
    mana_cost="{2}{G}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

cursed_mirror = Card(
    name="Cursed Mirror",
    mana_cost="{2}{R}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R"],
    text="""{T}: Add {R}.
As this artifact enters, you may have it become a copy of any creature on the battlefield until end of turn, except it has haste.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

deceptive_landscape = Card(
    name="Deceptive Landscape",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add {C}.
{T}, Sacrifice this land: Search your library for a basic Plains, Swamp, or Forest card, put it onto the battlefield tapped, then shuffle.
Cycling {W}{B}{G} ({W}{B}{G}, Discard this card: Draw a card.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

despark = Card(
    name="Despark",
    mana_cost="{W}{B}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "W"],
    text="""Exile target permanent with mana value 4 or greater.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

dragonlord_dromoka = Card(
    name="Dragonlord Dromoka",
    mana_cost="{4}{G}{W}",
    card_type="Legendary Creature — Elder Dragon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "W"],
    text="""This spell can't be countered.
Flying, lifelink
Your opponents can't cast spells during your turn.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

duskdawn = SplitCard(
    name="Dusk // Dawn",
    left_name="Dusk",
    right_name="Dawn",
    left_type="Sorcery",
    right_type="Sorcery"
)

evolving_wilds = Card(
    name="Evolving Wilds",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}, Sacrifice this land: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

exotic_orchard = Card(
    name="Exotic Orchard",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add one mana of any color that a land an opponent controls could produce.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

expel_the_interlopers = Card(
    name="Expel the Interlopers",
    mana_cost="{3}{W}{W}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Choose a number between 0 and 10. Destroy all creatures with power greater than or equal to the chosen number.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

faeburrow_elder = Card(
    name="Faeburrow Elder",
    mana_cost="{1}{G}{W}",
    card_type="Creature — Treefolk Druid",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "W"],
    text="""Vigilance
This creature gets +1/+1 for each color among permanents you control.
{T}: For each color among permanents you control, add one mana of that color.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

farseek = Card(
    name="Farseek",
    mana_cost="{1}{G}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Search your library for a Plains, Island, Swamp, or Mountain card, put it onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

feed_the_swarm = Card(
    name="Feed the Swarm",
    mana_cost="{1}{B}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

felidar_retreat = Card(
    name="Felidar Retreat",
    mana_cost="{3}{W}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Landfall — Whenever a land you control enters, choose one —
• Create a 2/2 white Cat Beast creature token.
• Put a +1/+1 counter on each creature you control. Those creatures gain vigilance until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

feline_sovereign = Card(
    name="Feline Sovereign",
    mana_cost="{2}{G}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Other Cats you control get +1/+1 and have protection from Dogs.
Whenever one or more Cats you control deal combat damage to a player, destroy up to one target artifact or enchantment that player controls.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

felothar_the_steadfast = Card(
    name="Felothar the Steadfast",
    mana_cost="{1}{W}{B}{G}",
    card_type="Legendary Creature — Human Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "G", "W"],
    text="""Each creature you control assigns combat damage equal to its toughness rather than its power.
Creatures you control can attack as though they didn't have defender.
{3}, {T}, Sacrifice another creature: Draw cards equal to the sacrificed creature's toughness, then discard cards equal to its power.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

fleetfoot_panther = Card(
    name="Fleetfoot Panther",
    mana_cost="{1}{G}{W}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "W"],
    text="""Flash
When this creature enters, return a green or white creature you control to its owner's hand.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

forest = Card(
    name="Forest",
    mana_cost="",
    card_type="Basic Land — Forest",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {G}.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

fortified_village = Card(
    name="Fortified Village",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""As this land enters, you may reveal a Forest or Plains card from your hand. If you don't, this land enters tapped.
{T}: Add {G} or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

game_trail = Card(
    name="Game Trail",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""As this land enters, you may reveal a Mountain or Forest card from your hand. If you don't, this land enters tapped.
{T}: Add {R} or {G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

greater_tanuki = Card(
    name="Greater Tanuki",
    mana_cost="{4}{G}{G}",
    card_type="Enchantment Creature — Dog",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Trample
Channel — {2}{G}, Discard this card: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

heralds_horn = Card(
    name="Herald's Horn",
    mana_cost="{3}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""As this artifact enters, choose a creature type.
Creature spells you cast of the chosen type cost {1} less to cast.
At the beginning of your upkeep, look at the top card of your library. If it's a creature card of the chosen type, you may reveal it and put it into your hand.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

highcliff_felidar = Card(
    name="Highcliff Felidar",
    mana_cost="{5}{W}{W}",
    card_type="Creature — Cat Beast",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Vigilance
When this creature enters, for each opponent, choose a creature with the greatest power among creatures that player controls. Destroy those creatures.""",
    own_by="player",
    control_by="player",
    mana_value=7.0
)

hornet_nest = Card(
    name="Hornet Nest",
    mana_cost="{2}{G}",
    card_type="Creature — Insect",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender (This creature can't attack.)
Whenever this creature is dealt damage, create that many 1/1 green Insect creature tokens with flying and deathtouch. (Any amount of damage a creature with deathtouch deals to a creature is enough to destroy it.)""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

hungry_lynx = Card(
    name="Hungry Lynx",
    mana_cost="{1}{G}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Cats you control have protection from Rats. (They can't be blocked, targeted, or dealt damage by Rats.)
At the beginning of your end step, target opponent creates a 1/1 black Rat creature token with deathtouch.
Whenever a Rat dies, put a +1/+1 counter on each Cat you control.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

ikra_shidiqi_the_usurper = Card(
    name="Ikra Shidiqi, the Usurper",
    mana_cost="{3}{B}{G}",
    card_type="Legendary Creature — Snake Wizard",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "G"],
    text="""Menace
Whenever a creature you control deals combat damage to a player, you gain life equal to that creature's toughness.
Partner (You can have two commanders if both have partner.)""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

impact_tremors = Card(
    name="Impact Tremors",
    mana_cost="{1}{R}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R"],
    text="""Whenever a creature you control enters, this enchantment deals 1 damage to each opponent.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

indomitable_ancients = Card(
    name="Indomitable Ancients",
    mana_cost="{2}{W}{W}",
    card_type="Creature — Treefolk Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

indulging_patrician = Card(
    name="Indulging Patrician",
    mana_cost="{1}{W}{B}",
    card_type="Creature — Vampire Noble",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "W"],
    text="""Flying
Lifelink (Damage dealt by this creature also causes you to gain that much life.)
At the beginning of your end step, if you gained 3 or more life this turn, each opponent loses 3 life.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

infernal_grasp = Card(
    name="Infernal Grasp",
    mana_cost="{1}{B}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Destroy target creature. You lose 2 life.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

isolated_chapel = Card(
    name="Isolated Chapel",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control a Plains or a Swamp.
{T}: Add {W} or {B}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

jaddi_offshoot = Card(
    name="Jaddi Offshoot",
    mana_cost="{G}",
    card_type="Creature — Plant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
Landfall — Whenever a land you control enters, you gain 1 life.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

jaws_of_defeat = Card(
    name="Jaws of Defeat",
    mana_cost="{3}{B}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Whenever a creature you control enters, target opponent loses life equal to the difference between that creature's power and its toughness.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

jazal_goldmane = Card(
    name="Jazal Goldmane",
    mana_cost="{2}{W}{W}",
    card_type="Legendary Creature — Cat Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""First strike (This creature deals combat damage before creatures without first strike.)
{3}{W}{W}: Attacking creatures you control get +X/+X until end of turn, where X is the number of attacking creatures.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

jetmirs_garden = Card(
    name="Jetmir's Garden",
    mana_cost="",
    card_type="Land — Mountain Forest Plains",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {R}, {G}, or {W}.)
This land enters tapped.
Cycling {3} ({3}, Discard this card: Draw a card.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

jetmir_nexus_of_revels = Card(
    name="Jetmir, Nexus of Revels",
    mana_cost="{1}{R}{G}{W}",
    card_type="Legendary Creature — Cat Demon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""Creatures you control get +1/+0 and have vigilance as long as you control three or more creatures.
Creatures you control also get +1/+0 and have trample as long as you control six or more creatures.
Creatures you control also get +1/+0 and have double strike as long as you control nine or more creatures.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

jinnie_fay_jetmirs_second = Card(
    name="Jinnie Fay, Jetmir's Second",
    mana_cost="{R/G}{G}{G/W}",
    card_type="Legendary Creature — Elf Druid",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""If you would create one or more tokens, you may instead create that many 2/2 green Cat creature tokens with haste or that many 3/1 green Dog creature tokens with vigilance.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

jungle_shrine = Card(
    name="Jungle Shrine",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
{T}: Add {R}, {G}, or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

keeper_of_fables = Card(
    name="Keeper of Fables",
    mana_cost="{3}{G}{G}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Whenever one or more non-Human creatures you control deal combat damage to a player, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

king_of_the_pride = Card(
    name="King of the Pride",
    mana_cost="{2}{W}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Other Cats you control get +2/+1.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

kitt_kanto_mayhem_diva = Card(
    name="Kitt Kanto, Mayhem Diva",
    mana_cost="{1}{R}{G}{W}",
    card_type="Legendary Creature — Cat Bard Druid",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""When Kitt Kanto enters, create a 1/1 green and white Citizen creature token.
At the beginning of combat on each player's turn, you may tap two untapped creatures you control. When you do, target creature that player controls gets +2/+2 and gains trample until end of turn. Goad that creature.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

komainu_battle_armor = Card(
    name="Komainu Battle Armor",
    mana_cost="{2}{R}",
    card_type="Artifact Creature — Equipment Dog",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R"],
    text="""Menace
Equipped creature gets +2/+2 and has menace.
Whenever this creature or equipped creature deals combat damage to a player, goad each creature that player controls.
Reconfigure {4} ({4}: Attach to target creature you control; or unattach from a creature. Reconfigure only as a sorcery. While attached, this isn't a creature.)""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

krosan_verge = Card(
    name="Krosan Verge",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
{T}: Add {C}.
{2}, {T}, Sacrifice this land: Search your library for a Forest card and a Plains card, put them onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

lion_sash = Card(
    name="Lion Sash",
    mana_cost="{1}{W}",
    card_type="Artifact Creature — Equipment Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""{W}: Exile target card from a graveyard. If it was a permanent card, put a +1/+1 counter on this permanent.
Equipped creature gets +1/+1 for each +1/+1 counter on this Equipment.
Reconfigure {2} ({2}: Attach to target creature you control; or unattach from a creature. Reconfigure only as a sorcery. While attached, this isn't a creature.)""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

loyal_warhound = Card(
    name="Loyal Warhound",
    mana_cost="{1}{W}",
    card_type="Creature — Dog",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Vigilance
When this creature enters, if an opponent controls more lands than you, search your library for a basic Plains card, put it onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

lurking_predators = Card(
    name="Lurking Predators",
    mana_cost="{4}{G}{G}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Whenever an opponent casts a spell, reveal the top card of your library. If it's a creature card, put it onto the battlefield. Otherwise, you may put that card on the bottom of your library.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

marisi_breaker_of_the_coil = Card(
    name="Marisi, Breaker of the Coil",
    mana_cost="{1}{R}{G}{W}",
    card_type="Legendary Creature — Cat Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""Your opponents can't cast spells during combat.
Whenever a creature you control deals combat damage to a player, goad each creature that player controls. (Until your next turn, those creatures attack each combat if able and attack a player other than you if able.)""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

masked_vandal = Card(
    name="Masked Vandal",
    mana_cost="{1}{G}",
    card_type="Creature — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Changeling (This card is every creature type.)
When this creature enters, you may exile a creature card from your graveyard. If you do, exile target artifact or enchantment an opponent controls.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

maskwood_nexus = Card(
    name="Maskwood Nexus",
    mana_cost="{4}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Creatures you control are every creature type. The same is true for creature spells you control and creature cards you own that aren't on the battlefield.
{3}, {T}: Create a 2/2 blue Shapeshifter creature token with changeling. (It is every creature type.)""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

mirror_entity = Card(
    name="Mirror Entity",
    mana_cost="{2}{W}",
    card_type="Creature — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Changeling (This card is every creature type.)
{X}: Until end of turn, creatures you control have base power and toughness X/X and gain all creature types.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

mountain = Card(
    name="Mountain",
    mana_cost="",
    card_type="Basic Land — Mountain",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {R}.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

nacatl_warpride = Card(
    name="Nacatl War-Pride",
    mana_cost="{3}{G}{G}{G}",
    card_type="Creature — Cat Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""This creature must be blocked by exactly one creature if able.
Whenever this creature attacks, create X tokens that are copies of it and that are tapped and attacking, where X is the number of creatures defending player controls. Exile the tokens at the beginning of the next end step.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

natures_lore = Card(
    name="Nature's Lore",
    mana_cost="{1}{G}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Search your library for a Forest card, put that card onto the battlefield, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

nyxfleece_ram = Card(
    name="Nyx-Fleece Ram",
    mana_cost="{1}{W}",
    card_type="Enchantment Creature — Sheep",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""At the beginning of your upkeep, you gain 1 life.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

oketras_monument = Card(
    name="Oketra's Monument",
    mana_cost="{3}",
    card_type="Legendary Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""White creature spells you cast cost {1} less to cast.
Whenever you cast a creature spell, create a 1/1 white Warrior creature token with vigilance.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

oreskos_explorer = Card(
    name="Oreskos Explorer",
    mana_cost="{1}{W}",
    card_type="Creature — Cat Scout",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""When this creature enters, search your library for up to X Plains cards, where X is the number of players who control more lands than you. Reveal those cards, put them into your hand, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

orzhov_signet = Card(
    name="Orzhov Signet",
    mana_cost="{2}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{1}, {T}: Add {W}{B}.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

overgrown_battlement = Card(
    name="Overgrown Battlement",
    mana_cost="{1}{G}",
    card_type="Creature — Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
{T}: Add {G} for each creature you control with defender.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

overgrown_farmland = Card(
    name="Overgrown Farmland",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control two or more other lands.
{T}: Add {G} or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

pack_leader = Card(
    name="Pack Leader",
    mana_cost="{1}{W}",
    card_type="Creature — Dog",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Other Dogs you control get +1/+1.
Whenever this creature attacks, prevent all combat damage that would be dealt this turn to Dogs you control.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

path_of_ancestry = Card(
    name="Path of Ancestry",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
{T}: Add one mana of any color in your commander's color identity. When that mana is spent to cast a creature spell that shares a creature type with your commander, scry 1. (Look at the top card of your library. You may put that card on the bottom.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

path_to_exile = Card(
    name="Path to Exile",
    mana_cost="{W}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Exile target creature. Its controller may search their library for a basic land card, put that card onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

phabine_bosss_confidant = Card(
    name="Phabine, Boss's Confidant",
    mana_cost="{3}{R}{G}{W}",
    card_type="Legendary Creature — Cat Advisor",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""Creature tokens you control have haste.
Parley — At the beginning of combat on your turn, each player reveals the top card of their library. For each land card revealed this way, you create a 1/1 green and white Citizen creature token. Then creatures you control get +1/+1 until end of turn for each nonland card revealed this way. Then each player draws a card.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

plains = Card(
    name="Plains",
    mana_cost="",
    card_type="Basic Land — Plains",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {W}.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

protector_of_the_wastes = Card(
    name="Protector of the Wastes",
    mana_cost="{4}{W}{W}",
    card_type="Creature — Dragon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flying
When this creature enters or becomes monstrous, exile up to two target artifacts and/or enchantments controlled by different players.
{4}{W}: Monstrosity 3. (If this creature isn't monstrous, put three +1/+1 counters on it and it becomes monstrous.)""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

qasali_slingers = Card(
    name="Qasali Slingers",
    mana_cost="{4}{G}",
    card_type="Creature — Cat Warrior",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Reach
Whenever this creature or another Cat you control enters, you may destroy target artifact or enchantment.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

radiant_grove = Card(
    name="Radiant Grove",
    mana_cost="",
    card_type="Land — Forest Plains",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {G} or {W}.)
This land enters tapped.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

rampart_architect = Card(
    name="Rampart Architect",
    mana_cost="{3}{G}",
    card_type="Creature — Elephant Advisor",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Whenever this creature enters or attacks, create a 1/3 white Wall creature token with defender.
Whenever a creature you control with defender dies, you may search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

realmwalker = Card(
    name="Realmwalker",
    mana_cost="{2}{G}",
    card_type="Creature — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Changeling (This card is every creature type.)
As this creature enters, choose a creature type.
You may look at the top card of your library any time.
You may cast creature spells of the chosen type from the top of your library.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

regal_caracal = Card(
    name="Regal Caracal",
    mana_cost="{3}{W}{W}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Other Cats you control get +1/+1 and have lifelink. (Damage dealt by those creatures also causes you to gain that much life.)
When this creature enters, create two 1/1 white Cat creature tokens with lifelink.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

return_of_the_wildspeaker = Card(
    name="Return of the Wildspeaker",
    mana_cost="{4}{G}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Choose one —
• Draw cards equal to the greatest power among non-Human creatures you control.
• Non-Human creatures you control get +3/+3 until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

reunion_of_the_house = Card(
    name="Reunion of the House",
    mana_cost="{5}{W}{W}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Return any number of target creature cards with total power 10 or less from your graveyard to the battlefield. Exile Reunion of the House.""",
    own_by="player",
    control_by="player",
    mana_value=7.0
)

rhox_faithmender = Card(
    name="Rhox Faithmender",
    mana_cost="{3}{W}",
    card_type="Creature — Rhino Monk",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Lifelink (Damage dealt by this creature also causes you to gain that much life.)
If you would gain life, you gain twice that much life instead.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

rin_and_seri_inseparable = Card(
    name="Rin and Seri, Inseparable",
    mana_cost="{1}{R}{G}{W}",
    card_type="Legendary Creature — Dog Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "R", "W"],
    text="""Whenever you cast a Dog spell, create a 1/1 green Cat creature token.
Whenever you cast a Cat spell, create a 1/1 white Dog creature token.
{R}{G}{W}, {T}: Rin and Seri deals damage to any target equal to the number of Dogs you control. You gain life equal to the number of Cats you control.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

rootbound_crag = Card(
    name="Rootbound Crag",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control a Mountain or a Forest.
{T}: Add {R} or {G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

sandsteppe_citadel = Card(
    name="Sandsteppe Citadel",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
{T}: Add {W}, {B}, or {G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

scattered_groves = Card(
    name="Scattered Groves",
    mana_cost="",
    card_type="Land — Forest Plains",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {G} or {W}.)
This land enters tapped.
Cycling {2} ({2}, Discard this card: Draw a card.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

seedborn_muse = Card(
    name="Seedborn Muse",
    mana_cost="{3}{G}{G}",
    card_type="Creature — Spirit",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Untap all permanents you control during each other player's untap step.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

sehts_tiger = Card(
    name="Seht's Tiger",
    mana_cost="{2}{W}{W}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flash (You may cast this spell any time you could cast an instant.)
When this creature enters, you gain protection from the color of your choice until end of turn. (You can't be targeted, dealt damage, or enchanted by anything of the chosen color.)""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

selesnya_signet = Card(
    name="Selesnya Signet",
    mana_cost="{2}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{1}, {T}: Add {G}{W}.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

shadrix_silverquill = Card(
    name="Shadrix Silverquill",
    mana_cost="{3}{W}{B}",
    card_type="Legendary Creature — Elder Dragon",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B", "W"],
    text="""Flying, double strike
At the beginning of combat on your turn, you may choose two. Each mode must target a different player.
• Target player creates a 2/1 white and black Inkling creature token with flying.
• Target player draws a card and loses 1 life.
• Target player puts a +1/+1 counter on each creature they control.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

shalai_voice_of_plenty = Card(
    name="Shalai, Voice of Plenty",
    mana_cost="{3}{W}",
    card_type="Legendary Creature — Angel",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flying
You, planeswalkers you control, and other creatures you control have hexproof.
{4}{G}{G}: Put a +1/+1 counter on each creature you control.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

sheltered_thicket = Card(
    name="Sheltered Thicket",
    mana_cost="",
    card_type="Land — Mountain Forest",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {R} or {G}.)
This land enters tapped.
Cycling {2} ({2}, Discard this card: Draw a card.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

showdown_of_the_skalds = Card(
    name="Showdown of the Skalds",
    mana_cost="{2}{R}{W}",
    card_type="Enchantment — Saga",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R", "W"],
    text="""(As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.)
I — Exile the top four cards of your library. Until the end of your next turn, you may play those cards.
II, III — Whenever you cast a spell this turn, put a +1/+1 counter on target creature you control.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

sidar_kondo_of_jamuraa = Card(
    name="Sidar Kondo of Jamuraa",
    mana_cost="{2}{G}{W}",
    card_type="Legendary Creature — Human Knight",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G", "W"],
    text="""Flanking (Whenever a creature without flanking blocks this creature, the blocking creature gets -1/-1 until end of turn.)
Creatures your opponents control without flying or reach can't block creatures with power 2 or less.
Partner (You can have two commanders if both have partner.)""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

skullclamp = Card(
    name="Skullclamp",
    mana_cost="{1}",
    card_type="Artifact — Equipment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Equipped creature gets +1/-1.
Whenever equipped creature dies, draw two cards.
Equip {1}""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

skyhunter_strike_force = Card(
    name="Skyhunter Strike Force",
    mana_cost="{2}{W}",
    card_type="Creature — Cat Knight",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flying
Melee (Whenever this creature attacks, it gets +1/+1 until end of turn for each opponent you attacked this combat.)
Lieutenant — As long as you control your commander, other creatures you control have melee.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

slaughter_the_strong = Card(
    name="Slaughter the Strong",
    mana_cost="{1}{W}{W}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Each player chooses any number of creatures they control with total power 4 or less, then sacrifices all other creatures they control.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

sol_ring = Card(
    name="Sol Ring",
    mana_cost="{1}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add {C}{C}.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

spirited_companion = Card(
    name="Spirited Companion",
    mana_cost="{1}{W}",
    card_type="Enchantment Creature — Dog",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""When this creature enters, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

staff_of_compleation = Card(
    name="Staff of Compleation",
    mana_cost="{3}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}, Pay 1 life: Destroy target permanent you own.
{T}, Pay 2 life: Add one mana of any color.
{T}, Pay 3 life: Proliferate.
{T}, Pay 4 life: Draw a card.
{5}: Untap this artifact.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

stalking_leonin = Card(
    name="Stalking Leonin",
    mana_cost="{2}{W}",
    card_type="Creature — Cat Archer",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""When this creature enters, secretly choose an opponent.
Reveal the player you chose: Exile target creature that's attacking you if it's controlled by the chosen player. Activate only once.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

sungrass_prairie = Card(
    name="Sungrass Prairie",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{1}, {T}: Add {G}{W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

sunpetal_grove = Card(
    name="Sunpetal Grove",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control a Forest or a Plains.
{T}: Add {G} or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

swamp = Card(
    name="Swamp",
    mana_cost="",
    card_type="Basic Land — Swamp",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""({T}: Add {B}.)""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

swiftfoot_boots = Card(
    name="Swiftfoot Boots",
    mana_cost="{2}",
    card_type="Artifact — Equipment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Equipped creature has hexproof and haste. (It can't be the target of spells or abilities your opponents control. It can attack and {T} no matter when it came under your control.)
Equip {1} ({1}: Attach to target creature you control. Equip only as a sorcery.)""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

swords_to_plowshares = Card(
    name="Swords to Plowshares",
    mana_cost="{W}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Exile target creature. Its controller gains life equal to its power.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

sylvan_caryatid = Card(
    name="Sylvan Caryatid",
    mana_cost="{1}{G}",
    card_type="Creature — Plant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender, hexproof
{T}: Add one mana of any color.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

taurean_mauler = Card(
    name="Taurean Mauler",
    mana_cost="{2}{R}",
    card_type="Creature — Shapeshifter",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R"],
    text="""Changeling (This card is every creature type.)
Whenever an opponent casts a spell, you may put a +1/+1 counter on this creature.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

temple_of_malady = Card(
    name="Temple of Malady",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
When this land enters, scry 1. (Look at the top card of your library. You may put that card on the bottom.)
{T}: Add {B} or {G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

temple_of_plenty = Card(
    name="Temple of Plenty",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
When this land enters, scry 1. (Look at the top card of your library. You may put that card on the bottom.)
{T}: Add {G} or {W}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

temple_of_silence = Card(
    name="Temple of Silence",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped.
When this land enters, scry 1. (Look at the top card of your library. You may put that card on the bottom.)
{T}: Add {W} or {B}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

temur_sabertooth = Card(
    name="Temur Sabertooth",
    mana_cost="{2}{G}{G}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""{1}{G}: You may return another creature you control to its owner's hand. If you do, this creature gains indestructible until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

three_visits = Card(
    name="Three Visits",
    mana_cost="{1}{G}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Search your library for a Forest card, put it onto the battlefield, then shuffle.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

tip_the_scales = Card(
    name="Tip the Scales",
    mana_cost="{2}{B}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Sacrifice a creature. When you do, all creatures get -X/-X until end of turn, where X is the sacrificed creature's toughness.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

tocasias_welcome = Card(
    name="Tocasia's Welcome",
    mana_cost="{2}{W}",
    card_type="Enchantment",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Whenever one or more creatures you control with mana value 3 or less enter, draw a card. This ability triggers only once each turn.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

tower_defense = Card(
    name="Tower Defense",
    mana_cost="{1}{G}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Creatures you control get +0/+5 and gain reach until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

towering_titan = Card(
    name="Towering Titan",
    mana_cost="{4}{G}{G}",
    card_type="Creature — Giant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""This creature enters with X +1/+1 counters on it, where X is the total toughness of other creatures you control.
Sacrifice a creature with defender: All creatures gain trample until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=6.0
)

tree_of_redemption = Card(
    name="Tree of Redemption",
    mana_cost="{3}{G}",
    card_type="Creature — Plant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
{T}: Exchange your life total with this creature's toughness.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

twilight_mire = Card(
    name="Twilight Mire",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""{T}: Add {C}.
{B/G}, {T}: Add {B}{B}, {B}{G}, or {G}{G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

vanquishers_banner = Card(
    name="Vanquisher's Banner",
    mana_cost="{5}",
    card_type="Artifact",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""As this artifact enters, choose a creature type.
Creatures you control of the chosen type get +1/+1.
Whenever you cast a creature spell of the chosen type, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=5.0
)

wakestone_gargoyle = Card(
    name="Wakestone Gargoyle",
    mana_cost="{3}{W}",
    card_type="Creature — Gargoyle",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Defender, flying
{1}{W}: Creatures you control with defender can attack this turn as though they didn't have defender.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

walking_bulwark = Card(
    name="Walking Bulwark",
    mana_cost="{1}",
    card_type="Artifact Creature — Golem",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Defender
{2}: Until end of turn, target creature with defender gains haste, can attack as though it didn't have defender, and assigns combat damage equal to its toughness rather than its power. Activate only as a sorcery.""",
    own_by="player",
    control_by="player",
    mana_value=1.0
)

wall_of_blossoms = Card(
    name="Wall of Blossoms",
    mana_cost="{1}{G}",
    card_type="Creature — Plant Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
When this creature enters, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

wall_of_limbs = Card(
    name="Wall of Limbs",
    mana_cost="{2}{B}",
    card_type="Creature — Zombie Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Defender (This creature can't attack.)
Whenever you gain life, put a +1/+1 counter on this creature.
{5}{B}{B}, Sacrifice this creature: Target player loses X life, where X is this creature's power.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

wall_of_omens = Card(
    name="Wall of Omens",
    mana_cost="{1}{W}",
    card_type="Creature — Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Defender
When this creature enters, draw a card.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

wall_of_reverence = Card(
    name="Wall of Reverence",
    mana_cost="{3}{W}",
    card_type="Creature — Spirit Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Defender, flying
At the beginning of your end step, you may gain life equal to the power of target creature you control.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

wall_of_roots = Card(
    name="Wall of Roots",
    mana_cost="{1}{G}",
    card_type="Creature — Plant Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["G"],
    text="""Defender
Put a -0/-1 counter on this creature: Add {G}. Activate only once each turn.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

warp_world = Card(
    name="Warp World",
    mana_cost="{5}{R}{R}{R}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["R"],
    text="""Each player shuffles all permanents they own into their library, then reveals that many cards from the top of their library. Each player puts all artifact, creature, and land cards revealed this way onto the battlefield, then does the same for enchantment cards, then puts all cards revealed this way that weren't put onto the battlefield on the bottom of their library.""",
    own_by="player",
    control_by="player",
    mana_value=8.0
)

weathered_sentinels = Card(
    name="Weathered Sentinels",
    mana_cost="{3}",
    card_type="Artifact Creature — Wall",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""Defender, vigilance, reach, trample
This creature can attack players who attacked you during their last turn as though it didn't have defender.
Whenever this creature attacks, it gets +3/+3 and gains indestructible until end of turn.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

welcoming_vampire = Card(
    name="Welcoming Vampire",
    mana_cost="{2}{W}",
    card_type="Creature — Vampire",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flying
Whenever one or more other creatures you control with power 2 or less enter, draw a card. This ability triggers only once each turn.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

white_suns_zenith = Card(
    name="White Sun's Zenith",
    mana_cost="{X}{W}{W}{W}",
    card_type="Instant",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Create X 2/2 white Cat creature tokens. Shuffle White Sun's Zenith into its owner's library.""",
    own_by="player",
    control_by="player",
    mana_value=3.0
)

whitemane_lion = Card(
    name="Whitemane Lion",
    mana_cost="{1}{W}",
    card_type="Creature — Cat",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flash
When this creature enters, return a creature you control to its owner's hand.""",
    own_by="player",
    control_by="player",
    mana_value=2.0
)

will_of_the_abzan = Card(
    name="Will of the Abzan",
    mana_cost="{3}{B}",
    card_type="Sorcery",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["B"],
    text="""Choose one. If you control a commander as you cast this spell, you may choose both instead.
• Any number of target opponents each sacrifice a creature with the greatest power among creatures that player controls and lose 3 life.
• Return target creature card from your graveyard to the battlefield.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

wingmantle_chaplain = Card(
    name="Wingmantle Chaplain",
    mana_cost="{3}{W}",
    card_type="Creature — Human Cleric",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Defender
When this creature enters, create a 1/1 white Bird creature token with flying for each creature with defender you control.
Whenever another creature you control with defender enters, create a 1/1 white Bird creature token with flying.""",
    own_by="player",
    control_by="player",
    mana_value=4.0
)

woodland_cemetery = Card(
    name="Woodland Cemetery",
    mana_cost="",
    card_type="Land",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=[],
    text="""This land enters tapped unless you control a Swamp or a Forest.
{T}: Add {B} or {G}.""",
    own_by="player",
    control_by="player",
    mana_value=0.0
)

zetalpa_primal_dawn = Card(
    name="Zetalpa, Primal Dawn",
    mana_cost="{6}{W}{W}",
    card_type="Legendary Creature — Elder Dinosaur",
    subtype="",
    supertype="",
    mana_produced=[],
    color_id=["W"],
    text="""Flying, double strike, vigilance, trample, indestructible""",
    own_by="player",
    control_by="player",
    mana_value=8.0
)

