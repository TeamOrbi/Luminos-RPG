# Luminos's Rules and Engine
from __future__ import annotations
import random 
import re
from datetime import datetime
from zoneinfo import ZoneInfo

CLASSES = {
    "WARRIOR": {"hp": 42, "mana": 3, "attack": 11, "description": "tough, with strong attacks"},
    "MAGE": {"hp": 28, "mana": 12, "attack": 16, "description": "fragile, with powerful magic"},
    "ROGUE": {"hp": 34, "mana": 5, "attack": 13, "description": "balanced, quick and resourceful"},
    "PALADIN": {"hp": 40, "mana": 8, "attack": 10, "description": "a holy knight who protects and smites foes"},
    "RANGER": {"hp": 35, "mana": 6, "attack": 13, "description": "a skilled hunter who strikes from on high"},
    "CLERIC": {"hp": 32, "mana": 12, "attack": 10, "description": "a healer who uses sacred and holy magic to, well, heal"},
    "WARLOCK": {"hp": 30, "mana": 14, "attack": 12, "description": "a risky spellcaster who drains life from their enemies"},
    "BARD": {"hp": 33, "mana": 10, "attack": 11, "description": "a clever and skilled performer who mixes magic and music"},
}
#Abilities are unlocked by class, and level of player. Mana restored on REST.
ABILITIES = {
    "POWER STRIKE": {"class": "WARRIOR", "level": 1, "mana": 0, "damage": 1.8, "description": "a heavy weapon blow, shattering the bones of those hit by it"},
    "SHIELD BASH": {"class": "WARRIOR", "level": 3, "mana": 0, "damage": 1.4, "weaken": 2, "description": "a shield strike that weakens even the strongest of enemies"},
    "FIREBALL": {"class": "MAGE", "level": 1, "mana": 4, "damage": 2.0, "description": "a sudden burst of flame"},
    "ICE SHARD": {"class": "MAGE", "level": 3, "mana": 3, "damage": 1.6, "description": "a very sharp chunk of ice"},
    "BACKSTAB": {"class": "ROGUE", "level": 1, "mana": 0, "damage": 1.9, "description": "a precise strike, in the back to be specific"},
    "POISON BLADE": {"class": "ROGUE", "level": 3, "mana": 2, "damage": 1.5, "weaken": 2, "description": "a poisoned strike that weakens even the strongest enemy"},
    "SMITE": {"class": "PALADIN", "level": 1, "mana": 3, "damage": 1.7, "description": "a holy smite"},
    "HOLY LIGHT": {"class": "PALADIN", "level": 3, "mana": 4, "heal": 16, "description": "healing from holy power"},
    "AIMED SHOT": {"class": "RANGER", "level": 1, "mana": 0, "damage": 1.7, "description": "a shot that was aimed a little better than usual"},
    "TRAP": {"class": "RANGER", "level": 3, "mana": 2, "damage": 1.25, "weaken": 3, "description": "it's a trap!"},
    "HOLY BOLT": {"class": "CLERIC", "level": 1, "mana": 3, "damage": 1.6, "description": "a bolt of sacred energy from the sky, or you"},
    "HEAL": {"class": "CLERIC", "level": 3, "mana": 5, "heal": 22, "description": "restores your health"},
    "SHADOW BOLT": {"class": "WARLOCK", "level": 1, "mana": 3, "damage": 1.8, "description": "a bolt of dark energy, straight from you"},
    "DRAIN LIFE": {"class": "WARLOCK", "level": 3, "mana": 5, "damage": 1.3, "drain": 10, "description": "steals the life right out of your enemy"},
    "DISSONANT NOTE": {"class": "BARD", "level": 1, "mana": 3, "damage": 1.5, "description": "a magicical musical note, that hurts to hear."},
    "INSPIRING SONG": {"class": "BARD", "level": 3, "mana": 4, "heal": 14, "description": "restores your health through the power of music"},
    #Abilities/Spells above lev 5
    "WHIRLWIND": {"class": "WARRIOR", "level": 5, "mana": 2, "damage": 2.2, "description": "a sweeping blow, to sweep your enemies off their feet."},
    "LAST STAND": {"class": "WARRIOR", "level": 7, "mana": 3, "damage": 2.7, "description": "a mighty finishing blow"},
    "LIGHTNING BOLT": {"class": "MAGE", "level": 5, "mana": 6, "damage": 2.5, "description": "a bolt of power from the sky, striking your enemy."},
    "METEOR": {"class": "MAGE", "level": 7, "mana": 9, "damage": 3.2, "description": "a devastating meteor strike from the heavens above"},
    "SHADOWSTEP": {"class": "ROGUE", "level": 5, "mana": 3, "damage": 2.4, "description": "a sudden strike from the shadows"},
    "EXECUTE": {"class": "ROGUE", "level": 7, "mana": 4, "damage": 3.0, "description": "a deadly precise strike"},
    "DIVINE STRIKE": {"class": "PALADIN", "level": 5, "mana": 5, "damage": 2.3, "description": "a powerful radiant blow from the heavens"},
    "SANCTUARY": {"class": "PALADIN", "level": 7, "mana": 6, "heal": 28, "description": "restores a large chunk of health"},
    "MULTISHOT": {"class": "RANGER", "level": 5, "mana": 3, "damage": 2.2, "description": "a volley of precise arrows"},
    "EXPLOSIVE ARROW": {"class": "RANGER", "level": 7, "mana": 5, "damage": 2.9, "description": "an arrow that bursts with flames and explosion"},
    "RESTORATION": {"class": "CLERIC", "level": 5, "mana": 6, "heal": 30, "description": "restores a great deal of health"},
    "JUDGEMENT": {"class": "CLERIC", "level": 7, "mana": 7, "damage": 2.7, "description": "a powerful blast of holy, sacred judgement"},
    "CURSE": {"class": "WARLOCK", "level": 5, "mana": 4, "damage": 2.0, "weaken": 4, "description": "damages and weakens even the strongest enemy"},
    "SOUL HARVEST": {"class": "WARLOCK", "level": 7, "mana": 7, "damage": 2.2, "drain": 18, "description": "damages a foe and steals the life from them"},
    "WAR CHANT": {"class": "BARD", "level": 5, "mana": 5, "damage": 2.0, "weaken": 3, "description": "a forceful song that rattles your foe, to their bones."},
    "HEROIC BALLAD": {"class": "BARD", "level": 7, "mana": 7, "heal": 26, "description": "a stirring ballad that restores health"},
}

# Enemy tuples are (name, health, attack, XP reward, gold reward).
# Higher-level enemies only appear once a character has reached their tier.
ENEMIES = [
    ("Goblin", 18, 6, 12, 8),
    ("Forest Wolf", 22, 7, 15, 10),
    ("Bandit", 26, 8, 18, 12),
    ("Skeleton", 28, 8, 20, 13),
    ("Giant Spider", 32, 9, 22, 14),
    ("Dire Wolf", 38, 11, 30, 18),
    ("Orc Brute", 42, 11, 32, 20),
    ("Dark Mage", 36, 14, 35, 23),
    ("Troll", 55, 13, 42, 26),
    ("Wraith", 48, 16, 46, 29),
    ("Ogre", 65, 17, 52, 33),
    ("Young Dragon", 80, 20, 75, 50),
]
ENEMY_MIN_LEVEL = {
    "Goblin": 1,
    "Forest Wolf": 1,
    "Bandit": 1,
    "Skeleton": 2,
    "Giant Spider": 2,
    "Dire Wolf": 3,
    "Orc Brute": 3,
    "Dark Mage": 4,
    "Troll": 5,
    "Wraith": 6,
    "Ogre": 7,
    "Young Dragon": 9,
}
ENEMY_BY_NAME = {enemy[0]: enemy for enemy in ENEMIES}
SHOP_ITEMS = {
    "HEALING POTION": {"price": 12, "description": "restores up to 25 HP in a single gulp", "kind": "healing_potion"},
    "MANA POTION": {"price": 15, "description": "restores up to 10 mana", "kind": "mana_potion"},
    "BOMB": {"price": 20, "description": "deals 20 damage during combat", "kind": "bomb"},
    "BRONZE SWORD": {"price": 25, "description": "+2 attack while equipped", "kind": "weapon", "bonus": 2},
    "IRON SWORD": {"price": 55, "description": "+4 attack while equipped", "kind": "weapon", "bonus": 4},
    "LEATHER ARMOUR": {"price": 30, "description": "reduces incoming hits by 2", "kind": "armour", "bonus": 2},
    "CHAINMAIL": {"price": 65, "description": "reduces incoming hits by 4", "kind": "armour", "bonus": 4},
    "GREATER HEALING POTION": {"price": 35, "description": "restores up to 50 HP when used", "kind": "greater_healing_potion", "restore": 50},
    "GREATER MANA POTION": {"price": 32, "description": "restores up to 20 mana when used", "kind": "greater_mana_potion", "restore": 20},
    "ELIXIR OF VIGOUR": {"price": 48, "description": "restores up to 25 HP and 10 mana points when used", "kind": "elixir"},
    "FIRE SCROLL": {"price": 28, "description": "deals 35 damage to your current enemy", "kind": "fire_scroll"},
    "MITHRIL SWORD": {"price": 105, "description": "+7 attack while equipped", "kind": "weapon", "bonus": 7},
    "RUNED STAFF": {"price": 115, "description": "+8 attack while equipped", "kind": "weapon", "bonus": 8},
    "PLATE ARMOUR": {"price": 105, "description": "reduces incoming hits by 6", "kind": "armour", "bonus": 6},
}

FREE_COMMANDS = {"HELP", "STATUS", "INVENTORY", "MAP", "LOCATIONS", "ABILITIES", "SPELLS", "SHOP"}
ACTIONS = {"EXPLORE", "ATTACK", "DEFEND", "POTION", "FLEE", "REST", "TRAVEL", "BUY", "USE MANA POTION", "USE BOMB"}

# Each location has a min level and its own enemy encounters. The enemy tier is checked as well, players should never meet enemies above their tier.
LOCATIONS = {
    "Luminos": {
        "min_level": 1,
        "description": "a rather safe town, with a inn and a busy and bustling market",
        "enemies": (),
        "explore_text": "Luminos is safe from monsters.To go somewhere, use TRAVEL followed by a destination to head out.",
    },
    "Whistling Woods": {
        "min_level": 1,
        "description": "a misty and mysterious wood, filled with old paths, and rustling trees.",
        "enemies": {"Goblin", "Forest Wolf", "Bandit", "Dire Wolf"},
        "explore_text": "You follow a winding path beneath the whistling branches.",
    },
    "Goblin Caves": {
        "min_level": 2,
        "description": "a network of damp tunnels, spider webs and abandoned mine shafts",
        "enemies": {"Goblin", "Skeleton", "Giant Spider", "Orc Brute", "Troll"},
        "explore_text": "Your footsteps echo through the dark caves",
    },
    "Haunted Ruins": {
        "min_level": 3,
        "description": "crumbling halls haunted by restless spirits and forgotten magic",
        "enemies": {"Skeleton", "Bandit", "Dark Mage", "Wraith", "Ogre"},
        "explore_text": "You search the shattered halls of the haunted ruins",
    },
    "Frostfang Mountains": {
        "min_level": 4,
        "description": "a frozen mountain range battered by icy winds",
        "enemies": {"Dire Wolf", "Orc Brute", "Dark Mage", "Troll", "Ogre", "Wraith"},
        "explore_text": "You climb a narrow trail through the freezing mountain pass",
    },
    "Dragon's Lair": {
        "min_level": 9,
        "description": "a scorched cavern deep beneath a fiery volcano",
        "enemies": {"Wraith", "Ogre", "Young Dragon"},
        "explore_text": "Heat shimmers over the scorched stone of the dragon's lair. Perils Lie Within.",
    },
}
LOCATION_ALIASES = {
    "LUMINOS": "Luminos",
    "TOWN": "Luminos",
    "WHISTLING WOODS": "Whistling Woods",
    "WOODS": "Whistling Woods",
    "FOREST": "Whistling Woods",
    "GOBLIN CAVES": "Goblin Caves",
    "CAVES": "Goblin Caves",
    "GOBLIN CAVE": "Goblin Caves",
    "HAUNTED RUINS": "Haunted Ruins",
    "RUINS": "Haunted Ruins",
    "FROSTFANG MOUNTAINS": "Frostfang Mountains",
    "MOUNTAINS": "Frostfang Mountains",
    "FROSTFANG": "Frostfang Mountains",
    "DRAGON'S LAIR": "Dragon's Lair",
    "DRAGONS LAIR": "Dragon's Lair",
    "DRAGON LAIR": "Dragon's Lair",
    "DRAGON": "Dragon's Lair",
}

def local_date(timezone_name: str = "Australia/Adelaide") -> str:
    try:
        return datetime.now(ZoneInfo(timezone_name)).date().isoformat()
    except Exception:
        return datetime.now().date().isoformat()

def command_from_email(subject: str, body: str) -> str:
    # Uses first unquoted, non empty body line, falls back to the subject if needed.
    lines = []
    for line in (body or "").replace("\r", "").split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(">"):
            continue
        if re.match(r"^(on .+wrote:|from:|sent:|to:|subject:|[-_]{3,})", stripped, re.I):
            break
        lines.append(stripped)
    if lines:
        return lines[0][:100].strip()
    return (subject or "").strip()[:100]

def _help() -> str:
    return ("Commands you can email me:\n"
            "EXPLORE - venture out and find trouble or treasure\n"
            "ATTACK - strike your current enemy\n"
            "DEFEND - reduce the next enemy hit\n"
            "POTION - restore health (if you have one)\n"
            "SHOP - browse the Luminos market (free)\n"
            "BUY <item> - purchase a item in Luminos (uses today's action\n"
            "USE MANA POTION - restore mana"
            "USE BOMB - deal damage during combat"
            "FLEE - leave a fight\n"
            "REST - recover some health when you are not in combat\n"
            "TRAVEL <location> - move to another area (uses today's action)\n"
            "MAP or LOCATIONS - see destinations and level requirements\n"
            "ABILITIES or SPELLS - list your class abilities (free)\n"
            "CAST <name> or ABILITY <name> - use a class ability in combat\n"
            "STATUS or INVENTORY - free, do not use your daily action\n\n"
            "Destinations: Luminos, Whistling Woods, Goblin Caves, Haunted Ruins, Frostfang Mountains, Dragon's Lair.\n"
            "You may make one game-changing action per local calendar day. Status, inventory, map, shop, abilities and help are free.")

def _status(p) -> str:
    enemy = f"\nEnemy: {p['enemy_name']} ({p['enemy_hp']} HP)" if p["enemy_name"] else "\nYou are not in combat."
    return (f"{p['name']} the {p['class'].title()}\nLevel {p['level']} | XP {p['xp']} | Gold {p['gold']}\n"
            f"Health: {p['hp']}/{p['max_hp']} | Mana: {p['mana']}/{p['max_mana']} | Potions: {p['potions']}\nLocation: {p['location']}{enemy}")

def _inventory(conn, p) -> str:
    rows = conn.execute("SELECT item, quantity FROM player_items WHERE email=? AND quantity>0 ORDER BY item", (p["email"],)).fetchall()
    items = [f"- {row['item'].title()}: {row['quantity']}" for row in rows]
    if not items:
        items = ["- No other items"]
    return (f"Inventory\n- Healing potions: {p['potions']}\n" + "\n".join(items) +
           f"\n- Equipped weapon: {p['weapon'] or 'None'} (+{p['attack_bonus']} attack)" +
           f"\n- Equipped armour: {p['armour'] or 'None'} (reduces hits by {p['armour_bonus']})" +
           f"\n- Gold: {p['gold']}\n- Mana: {p['mana']}/{p['max_mana']}")

def _shop() -> str:
    lines = ["Luminos Market (SHOP is free; BUY uses your daily action):"]
    for name, item in SHOP_ITEMS.items():
        lines.append(f"- {name.title()} - {item['price']} gold; {item['description']}.")
    lines.append("\nBuy a item by emailing BUY followed by its name. e.g. BUY MANA POTION.")
    lines.append("The market is only available in Luminos. Weapons and armour equip automatically when purchased.")
    return "\n".join(lines)

def _abilities(p) -> str:
    lines = [f"Abilities for {p['name']} the {p['class'].title()}:"]
    for name, data in ABILITIES.items():
        if data["class"] != p["class"]:
            continue
        state = "available" if p["level"] >= data["level"] else f"unlocks at level {data['level']}"
        effect = f"{data['damage']:g}x attack damage" if "damage" in data else f"heals up to {data['heal']} HP"
        if "heal" in data and "damage" in data:
            effect += f" and heals up to {data['drain']} HP"
        lines.append(f"- {name} - {effect}; costs {data['mana']} mana; {state}")
    lines.append("\nIn combat, email CAST FIREBALL (or ABILITY POWER STRIKE). Ability use consumes your daily action.")
    return "\n".join(lines)

def _map(p) -> str:
    lines = [f"Luminos Map - you are currently in {p['location']}:"]
    for name, details in LOCATIONS.items():
        if name == p["location"]:
            marker = " [CURRENT LOCATION]"
        elif p["level"] < details["min_level"]:
            marker = f" [LOCKED until level {details['min_level']}]"
        else:
            marker = f" [available from level {details['min_level']}]"
        lines.append(f"- {name}{marker}: {details['description']}")
    lines.append("\nTo travel, email TRAVEL followed by the destination, for example: TRAVEL GOBLIN CAVES.")
    lines.append("Travelling uses your daily action. You cannot travel while in combat.")
    return "\n".join(lines)


def _level_up(conn, p, earned_xp: int) -> str:
    xp = p["xp"] + earned_xp
    level = p["level"]
    max_hp = p["max_hp"]
    max_mana = p["max_mana"]
    notes = []
    while xp >= level * 30:
        xp -= level * 30
        level += 1
        max_hp += 5
        max_mana += 2
        notes.append(f"Level up! You are now level {level}; maximum health increased to {max_hp} and maximum mana to {max_mana}.")
    conn.execute("UPDATE players SET xp=?, level=?, max_hp=?, max_mana=? WHERE email=?", (xp, level, max_hp, max_mana, p["email"]))
    if notes:
        conn.execute("UPDATE players SET hp=?, mana=? WHERE email=?", (max_hp, max_mana, p["email"]))
    return "\n".join(notes)

def handle_email(conn, email: str, subject: str, body: str, timezone_name: str = "Australia/Adelaide") -> str:
    #Processes one message
    email = email.strip().lower()
    command = command_from_email(subject, body)
    upper = command.upper().strip()
    p = conn.execute("SELECT * FROM players WHERE email=?", (email,)).fetchone()

    if p is None:
        if upper in {"START", "START GAME", "PLAY", "BEGIN"}:
            conn.execute("INSERT INTO players(email, status) VALUES (?, 'awaiting_name')", (email,))
            return ("Welcome to Luminos, adventurer!\n\nFirst, what should your character be called? "
                    "Reply with a name between 2 and 20 characters. Use letters, numbers, spaces, apostrophes or hyphens.")
        return "To begin your own Luminos adventure, email START. Each email address gets its own character and save."

    if p["status"] == "awaiting_name":
        name = command.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 '\-]{0,19}", name) or len(name) < 2:
            return "That name isn't valid. Please reply with 2-20 characters: letters, numbers, spaces, apostrophes or hyphens."
        conn.execute("UPDATE players SET name=?, status='awaiting_class' WHERE email=?", (name, email))
        return (f"Great! {name}, your story begins now. Choose your class by replying with ONE, and ONLY ONE of these:\n\n"
                "WARRIOR - sturdy fighter; Power Strike\n"
                "MAGE - spellcaster; Fireball, Ice Shard at level 3\n"
                "ROGUE - agile striker; Backstab\n"
                "PALADIN - holy knight; Smite, Holy Light at level 3\n"
                "RANGER - hunter; Aimed Shot, Trap at level 3\n"
                "CLERIC - healer; Holy Bolt, Heal at level 3\n"
                "WARLOCK - dark magic; Shadow Bold, Drain Life at level 3\n"
                "BARD - magical support; Dissonant Note, Inspiring Song at level 3\n\n Reply with WARRIOR, MAGE, ROGUE, PALADIN, RANGER, CLERIC, WARLOCK or BARD.")

    if p["status"] == "awaiting_class":
        chosen = upper
        if chosen not in CLASSES:
            return "Please choose WARRIOR, MAGE, ROGUE, PALADIN, RANGER, CLERIC, WARLOCK or BARD."
        stats = CLASSES[chosen]
        conn.execute("UPDATE players SET class=?, status='playing', hp=?, max_hp=?, mana=?, max_mana=?, location='Whispering Woods' WHERE email=?",
                     (chosen, stats["hp"], stats["hp"], stats["mana"], stats["mana"], email))
        return (f"Your adventure begins, {p['name']} the {chosen.title()}!\n\n"
                f"You are {stats['description']}. You have {stats['hp']} HP, {stats['mana']} mana and 2 healing potions.\n\n"
                "You stand at the edge of the Whistling Woods. What will you do?\n"
                "Reply EXPLORE to begin. Email ABILITIES to see your powers. MAP, STATUS, INVENTORY, ABILITIES and HELP are free.\n\n" + _help())

    if upper in FREE_COMMANDS:
        if upper == "HELP":
            return _help()
        if upper == "SHOP":
            if p["location"] != "Luminos":
                return "The market is in Luminos. Email TRAVEL LUMINOS to head over there, then SHOP. No daily acton was used."
            return _shop()
        if upper in {"ABILITIES", "SPELLS"}:
            return _abilities(p)
        if upper == "STATUS":
            return _status(p)
        if upper == "MAP" or upper == "LOCATIONS":
            return _map(p)
        return _inventory(conn, p)

    ability_name = upper[5:].strip() if upper.startswith("CAST ") else (upper[7:].strip() if upper.startswith("ABILITY ") else None)
    buy_item = upper[4:].strip() if upper.startswith("BUY ") else None
    use_item = upper[4:].strip() if upper.startswith("USE ") else None
    if upper == "BUY":
        return "What would you like to buy? Email SHOP for the list, then BUY followed by the item name. No daily action was used."
    if buy_item and buy_item not in SHOP_ITEMS:
        return f"I don't recognise '{buy_item}'. Email SHOP to see available items. No daily action was used."
    if upper == "USE":
        return "What would you like to use? Try USE MANA POTION or USE BOMB. No daily action was used."
    usable_items = {"MANA POTION", "BOMB", "GREATER HEALING POTION", "GREATER MANA POTION", "ELIXIR OF VIGOUR", "FIRE SCROLL"}
    if use_item and use_item not in usable_items:
        return "You can use MANA POTION, GREATER MANA POTION, GREATER HEALING POTION, ELIXIR OF VIGOUR, BOMB or FIRE SCROLL. Healing potions can also be used with POTION. No daily action was used."

    travel_destination = None
    if upper.startswith("TRAVEL "):
        requested_destination = upper[len("TRAVEL "):].strip().replace("'", "'")
        travel_destination = LOCATION_ALIASES.get(requested_destination)
        if travel_destination is None:
            return "I couldn't identify that destination. Email MAP for the list of locations. No daily action was used."
    elif upper == "TRAVEL":
        return "Where would you like to travel? Reply TRAVEL followed by a destination, such as TRAVEL HAUNTED RUINS. Email MAP for destinations. No daily action was used."

    if upper not in ACTIONS and travel_destination is None and ability_name is None and buy_item  is None:
        return "I didn't recognise that command.\n\n" + _help()

    ability = ABILITIES.get(ability_name) if ability_name else None
    if ability_name and ability is None:
        return f"I don't know the ability '{ability_name}'. Email ABILITIES to see your options. No daily action was used."
    if ability and ability["class"] != p["class"]:
        return f"Only a {ability['class'].title()} can use (ability_name). Email ABILITIES to see your class abilities. No daily action was used."
    if ability and p["level"] < ability["level"]:
        return f"{ability_name} unlocks at level {ability['level']}. No daily action was used."
    if ability and p["mana"] < ability["mana"]:
        return f"You need {ability['mana']} mana to use {ability_name}, but have {p['mana']}. REST to recover mana. No daily action was used."

    # Check whether this command is valid in the current situation before spending the daily turn.
    if (upper in {"ATTACK", "DEFEND", "POTION", "FLEE", "USE BOMB"} or ability_name) and not p["enemy_name"]:
        return "There is no enemy here right now. Reply EXPLORE to look for an adventure. No daily action was used."
    if buy_item and p["location"] != "Luminos":
        return "You must be in ELuminos to shop. Email TRAVEL LUMINOS to return. No daily action was used."
    if buy_item and p["gold"] < SHOP_ITEMS[buy_item]["price"]:
        return f"{buy_item.title()} costs {SHOP_ITEMS[buy_item]['price']} gold, but you only have {p['gold']}. No daily action was used."
    if buy_item and SHOP_ITEMS[buy_item]["kind"] == "weapon" and SHOP_ITEMS[buy_item]["bonus"] <= p["attack_bonus"]:
        return "You already have an equally good or better weapon equipped. No daily action was used."
    if buy_item and SHOP_ITEMS[buy_item]["kind"] == "armour" and SHOP_ITEMS[buy_item]["bonus"] <= p["armour_bonus"]:
        return "You already have equally good or better armour equipped. No daily action was used."
    if use_item in {"MANA POTION", "GREATER MANA POTION"} and p["mana"] >= p["max_mana"]:
        return "Your mana is already full. No daily action was used."
    if use_item == "GREATER HEALING POTION" and p["hp"] >= p["max_hp"]:
        return "Your health is already full. No daily action was used."
    if use_item == "ELIXIR OF VIGOUR" and p["hp"] >= p["max_hp"] and p["mana"] >= p["max_mana"]:
        return "Your health and mana are already full. No daily action was used."
    if use_item in {"MANA POTION", "GREATER MANA POTION", "GREATER HEALING POTION", "ELIXIR OF VIGOUR", "BOMB", "FIRE SCROLL"}:
        item_row = conn.execute("SELECT quantity FROM player_items WHERE email=? AND item=?", (email, use_item)).fetchone()
        if item_row is None or item_row["quantity"] < 1:
            display_name = use_item.lower() if use_item == "BOMB" else use_item.title()
            return f"You don't have a {display_name}. Buy one in Luminos. No daily action was used."
    if use_item in {"BOMB", "FIRE SCROLL"} and not p["enemy_name"]:
        return "That item can only be used during combat. No daily action was used."
    if ability and "heal" in ability and p["hp"] >= p["max_hp"]:
        return "You are already at full health. No daily action was used."
    if upper == "EXPLORE" and p["enemy_name"]:
        return "You're already in a fight! Reply ATTACK, DEFEND, POTION or FLEE. No daily action was used."
    if upper == "EXPLORE" and p["location"] == "Luminos":
        return "Luminos is a safe town, so there are no monsters to fight here. Reply TRAVEL WHISTLING WOODS to head out. No daily action was used."
    if travel_destination is not None and p["enemy_name"]:
        return "You cannot travel while a enemy is blocking your path. Reply ATTACK, DEFEND, POTION or FLEE first. No daily action was used."
    if travel_destination is not None and p["level"] < LOCATIONS[travel_destination]["min_level"]:
        return (f"{travel_destination} is too dangerous for you right now. You need to reach level "
                f"{LOCATIONS[travel_destination]['min_level']} first. No daily action was used.")
    if travel_destination == p["location"]:
        return "You're already there! Choose another destination from MAP. No daily action was used."
    if upper == "POTION" and p["potions"] <= 0:
        return "You have no healing potions left. No daily action was used."
    if upper == "POTION" and p["hp"] >= p["max_hp"]:
        return "You're already at full health. No daily action was used."
    if upper == "REST" and p["enemy_name"]:
        return "You cannot rest while a enemy is nearby. Use ATTACK, DEFEND, POTION or FLEE. No daily action was used."
    if upper == "REST" and p["hp"] >= p["max_hp"] and p["mana"] >= p["max_mana"]:
        return "You're already at full health and mana. No daily action was used."
    today = local_date(timezone_name)
    if p["last_action_date"] == today:
        return (f"You've already used today's action. Your next action is available after midnight in {timezone_name}.\n\n"
                "You can still email STATUS, INVENTORY or HELP for free.")

    conn.execute("UPDATE players SET last_action_date=? WHERE email=?", (today, email))
    # Refresh row after any changes made above
    p = conn.execute("SELECT * FROM players WHERE email=?", (email,)).fetchone()
    result = []

    if travel_destination is not None:
        conn.execute("UPDATE players SET location=? WHERE email=?", (travel_destination, email))
        result.append(f"You travel to {travel_destination}. It is {LOCATIONS[travel_destination]['description']}.")
        if LOCATIONS[travel_destination]["enemies"]:
            result.append("You have arrived safely. Reply EXPLORE tomorrow to search the area.")
        else:
            result.append("The town is safe. You can REST here to recover health, or use TRAVEL to leave.")
    elif upper == "EXPLORE":
        roll = random.random()
        location = LOCATIONS[p["location"]]
        if roll < 0.72:
            available_enemies = [
                ENEMY_BY_NAME[name]
                for name in location["enemies"]
                if ENEMY_MIN_LEVEL.get(name, 1) <= p["level"]
            ]
            name, hp, attack, xp_reward, gold_reward = random.choice(available_enemies)
            conn.execute("UPDATE players SET enemy_name=?, enemy_hp=?, enemy_attack=? WHERE email=?", (name, hp, attack, email))
            result.append(f"{location['explore_text']}, and a {name} blocks your path! It has {hp} HP.")
            result.append("Your next action can be ATTACK, DEFEND, POTION or FLEE.")
        elif roll < 0.88:
            found = random.randint(5, 14)
            conn.execute("UPDATE players SET gold=gold+? WHERE email=?", (found, email))
            result.append(f"While exploring {p['location']}, you find a small pouch containing {found} gold. No enemy appears today.")
        else:
            conn.execute("UPDATE players SET potions=potions+1 WHERE email=?", (email,))
            result.append(f"While exploring {p['location']}, you discover a healing potion and add it to your inventory.")
    elif buy_item:
        item = SHOP_ITEMS[buy_item]
        conn.execute("UPDATE players SET gold=gold-? WHERE email=?", (item["price"], email))
        if item["kind"] == "healing_potion":
            conn.execute("UPDATE players SET potions=potions+1 WHERE email=?", (email,))
            result.append("You buy a healing potion and add it to your inventory.")
        elif item["kind"] == "mana_potion":
            conn.execute("INSERT INTO player_items(email,item,quantity) VALUES (?, ?, 1) ON CONFLICT(email,item) DO UPDATE SET quantity=quantity+1", (email, buy_item))
            result.append("You buy a mana potion. Email USE MANA POTION to restore up to 10 mana.")
        elif item["kind"] in {"bomb", "greater_healing_potion", "greater_mana_potion", "elixir", "fire_scroll"}:
            conn.execute("INSERT INTO player_items(email,item,quantity) VALUES (?, ?, 1) ON CONFLICT(email,item) DO UPDATE SET quantity=quantity+1", (email, buy_item))
            item_messages = {
                "BOMB": "You buy a bomb. During combat, email USE BOMB to deal 20 damage.",
                "GREATER HEALING POTION": "You buy a Greater healing potion. Email USE GREATER HEALING POTION to restore up to 50 HP.",
                "GREATER MANA POTION": "You buy a greater mana potion. Email USE GREATER MANA POTION to restore up to 20 mana.",
                "ELIXIR OF VIGOUR": "You buy a elixir of vigour. It restores up to 25 HP and 10 mana when used.",
                "FIRE SCROLL": "You buy a fire scroll. During combat,  email USE FIRE SCROLL to deal 35 damage.",
            }
            result.append(item_messages[buy_item])
        elif item["kind"] == "weapon":
            conn.execute("UPDATE players SET weapon=?, attack_bonus=? WHERE email=?", (buy_item, item["bonus"], email))
            result.append(f"You buy and equip the {buy_item.title()}. Your attacks now gain +{item['bonus']} damage.")
        elif item["kind"] == "armour":
            conn.execute("UPDATE players SET armour=?, armour_bonus=? WHERE email=?", (buy_item, item["bonus"], email))
            result.append(f"You buy and equip {buy_item.title()}. Incoming enemy hits are reduced by {item['bonus']} damage (minimum 1).")
    elif use_item in {"MANA POTION", "GREATER MANA POTION", "GREATER HEALING POTION", "ELIXIR OF VIGOUR"}:
        restored_hp = 0
        restored_mana = 0
        if use_item == "MANA POTION":
            restored_mana = min(10, p["max_mana"] - p["mana"])
        elif use_item == "GREATER MANA POTION":
            restored_mana = min(20, p["max_mana"] - p["mana"])
        elif use_item == "GREATER HEALING POTION":
            restored_hp = min(50, p["max_hp"] - p["hp"])
        else:
            restored_hp = min(25, p["max_hp"] - p["hp"])
            restored_mana = min(10, p["max_mana"] - p["mana"])
        conn.execute("UPDATE players SET hp=hp+?, mana=mana+? WHERE email=?", (restored_hp, restored_mana, email))
        conn.execute("UPDATE player_items SET quantity=quantity-1 WHERE email=? AND item=?", (email, use_item))
        if use_item == "MANA POTION":
            result.append(f"You drink a mana potion and restore {restored_mana} mana.")
        else:
            result.append(f"You use {use_item.title()} and restore {restored_hp} HP and {restored_mana} mana.")
    elif upper in {"USE BOMB", "USE FIRE SCROLL"}:
        item_name = "BOMB" if upper == "USE BOMB" else "FIRE SCROLL"
        item_damage = 20 if item_name == "BOMB" else 35
        enemy_name = p["enemy_name"]
        enemy_hp = max(0, p["enemy_hp"] - item_damage)
        conn.execute("UPDATE player_items SET quantity=quantity-1 WHERE email=? AND item=?", (email, item_name))
        if item_name == "BOMB":
            result.append(f"You throw a bomb at the {enemy_name}, dealing {item_damage} damage.")
        else:
            result.append(f"You use a fire scroll against the {enemy_name}, dealing {item_damage} damage.")
        if enemy_hp <= 0:
            _, _, _, xp_reward, gold_reward = ENEMY_BY_NAME[enemy_name]
            conn.execute("UPDATE players SET enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=gold+? WHERE email=?", (gold_reward, email))
            result.append(f"You defeat the {enemy_name}! You earn {xp_reward} XP and {gold_reward} gold.")
            level_msg = _level_up(conn, p, xp_reward)
            if level_msg:
                result.append(level_msg)
        else:
            damage_taken = max(1, random.randint(1, max(2, p["enemy_attack"])) - p["armour_bonus"])
            new_hp = max(0, p["hp"] - damage_taken)
            conn.execute("UPDATE players SET enemy_hp=?, hp=? WHERE email=?", (enemy_hp, new_hp, email))
            result.append(f"The {enemy_name} hits back for {damage_taken} damage. You have {new_hp}/{p['max_hp']} HP left.")
            if new_hp == 0:
                conn.execute("UPDATE players SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Luminos' WHERE email=?", (max(1, p['max_hp']//2), email))
                result.append("You collapse and are carried back to Luminos, recovering to half health and losing 3 gold.")
    elif upper == "ATTACK" or ability_name:
        base = CLASSES[p["class"]]["attack"] + p["level"] - 1 + p["attack_bonus"]
        if ability_name:
            damage = max(1, int(base * ability["damage"])) if "damage" in ability else 0
            conn.execute("UPDATE players SET mana=mana-? WHERE email=?", (ability["mana"], email))
            result.append(f"You use {ability_name.title()}!")
            if "heal" in ability:
                current_hp = conn.execute("SELECT hp FROM players WHERE email=?", (email,)).fetchone()["hp"]
                restored = min(ability["heal"], p["max_hp"] - current_hp)
                conn.execute("UPDATE players SET hp=hp+? WHERE email=?", (restored, email))
                result.append(f"You recover {restored} HP.")
            if "damage" in ability:
                result.append(f"Your ability hits the {p['enemy_name']} for {damage} damage.")
        else:
            damage = random.randint(max(2, base - 3), base + 2)
        enemy_hp = max(0, p["enemy_hp"] - damage)
        if ability and ability.get("weaken") and enemy_hp > 0:
            weakened_attack = max(1, p["enemy_attack"] - ability["weaken"])
            conn.execute("UPDATE players SET enemy_attack=? WHERE email=?", (weakened_attack, email))
            result.append(f"The trap weakens the enemy's attack to {weakened_attack}.")
        if ability and ability.get("drain"):
            current_hp = conn.execute("SELECT hp FROM players WHERE email=?", (email,)).fetchone()["hp"]
            restored = min(ability["drain"], p["max_hp"] - current_hp)
            if restored:
                conn.execute("UPDATE players SET hp=hp+? WHERE email=?", (restored, email))
                result.append(f"You drain {restored} HP from the enemy.")
        if not ability_name:
            result.append(f"You attack the {p['enemy_name']} for {damage} damage.")
        if enemy_hp <= 0:
            enemy_name = p["enemy_name"]
            # Rewards for enemy drops come from enemy def, new enemies need no extra code.
            _, _, _, xp_reward, gold_reward = ENEMY_BY_NAME[enemy_name]
            conn.execute("UPDATE players SET enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=gold+? WHERE email=?", (gold_reward, email))
            result.append(f"You defeat the {enemy_name}! You earn {xp_reward} XP and {gold_reward} gold.")
            level_msg = _level_up(conn, p, xp_reward)
            if level_msg:
                result.append(level_msg)
        else:
            current_hp = conn.execute("SELECT hp FROM players WHERE email=?", (email,)).fetchone()["hp"]
            damage_taken = max(1, random.randint(1, max(2, p["enemy_attack"])) - p["armour_bonus"])
            new_hp = max(0, current_hp - damage_taken)
            conn.execute("UPDATE players SET enemy_hp=?, hp=? WHERE email=?", (enemy_hp, new_hp, email))
            result.append(f"The {p['enemy_name']} hits back for {damage_taken} damage. You have {new_hp}/{p['max_hp']} HP left.")
            if new_hp == 0:
                conn.execute("UPDATE players SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Luminos' WHERE email=?", (max(1, p["max_hp"] // 2), email))
                result.append("You collapse and are carried back to town. You recover half health and lose 3 gold, but your adventure... continues.")
    elif upper == "DEFEND":
        damage_taken = max(1, random.randint(1, max(2, p["enemy_attack"])) // 2 - p["armour_bonus"])
        new_hp = max(0, p["hp"] - damage_taken)
        conn.execute("UPDATE players SET hp=? WHERE email=?", (new_hp, email))
        result.append(f"You brace for the attack and take only {damage_taken} damage. Health: {new_hp}/{p['max_hp']}.")
        if new_hp == 0:
            conn.execute("UPDATE players SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Luminos' WHERE email=?", (max(1, p["max_hp"] // 2), email))
            result.append("You collapse and are carried back to town. You recover half health and lose 3 gold, but your adventure... continues.")
    elif upper == "POTION":
        restored = min(25, p["max_hp"] - p["hp"])
        new_hp = p["hp"] + restored
        conn.execute("UPDATE players SET hp=?, potions=potions-1 WHERE email=?", (new_hp, email))
        result.append(f"You drink a healing potion and recover {restored} HP. Health: {new_hp}/{p['max_hp']}.")
    elif upper == "FLEE":
        conn.execute("UPDATE players SET enemy_name=NULL, enemy_hp=0, enemy_attack=0 WHERE email=?", (email,))
        result.append(f"You escape from the {p['enemy_name']} and retreat to a safer spot in {p['location']}.")
    elif upper == "REST":
        restored = min(10, p["max_hp"] - p["hp"])
        mana_restored = p["max_mana"] - p["mana"]
        conn.execute("UPDATE players SET hp=?, mana=max_mana WHERE email=?", (p["hp"] + restored, email))
        result.append(f"You rest and recover {restored} HP and {mana_restored} mana. Health: {p['hp'] + restored}/{p['max_hp']}; mana: {p['max_mana']}/{p['max_mana']}.")

    latest = conn.execute("SELECT * FROM players WHERE email=?", (email,)).fetchone()
    result.append(f"\nCurrent status: {latest['hp']}/{latest['max_hp']} HP, {latest['mana']}/{latest['max_mana']} mana, level {latest['level']}, {latest['gold']} gold.")
    result.append("Your next game-changing action is available tomorrow. STATUS, INVENTORY, MAP, ABILITIES and HELP are free.")
    return "\n\n".join(result)
