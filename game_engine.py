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
FREE_COMMANDS = {"HELP", "STATUS", "INVENTORY", "MAP", "LOCATIONS", "ABILITIES", "SPELLS"}
ACTIONS = {"EXPLORE", "ATTACK", "DEFEND", "POTION", "FLEE", "REST", "TRAVEL"}

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
            "FLEE - leave a fight\n"
            "REST - recover some health when you are not in combat\n"
            "TRAVEL <location> - move to another area (uses today's action)\n"
            "MAP or LOCATIONS - see destinations and level requirements\n"
            "ABILITIES or SPELLS - list your class abilities (free)\n"
            "CAST <name> or ABILITY <name> - use a class ability in combat\n"
            "STATUS or INVENTORY - free, do not use your daily action\n\n"
            "Destinations: Luminos, Whistelling Woods, Goblin Caves, Haunted Ruins, Frostfang Mountains, Dragon's Lair.\n"
            "You may make one game-changing action per local calendar day. Status, inventory, map, abilities and help are free.")

def _status(p) -> str:
    enemy = f"\nEnemy: {p['enemy_name']} ({p['enemy_hp']} HP)" if p["enemy_name"] else "\nYou are not in combat."
    return (f"{p['name']} the {p['class'].title()}\nLevel {p['level']} | XP {p['xp']} | Gold {p['gold']}\n"
            f"Health: {p['hp']}/{p['max_hp']} | Mana: {p['mana']}/{p['max_mana']} | Potions: {p['potions']}\nLocation: {p['location']}{enemy}")

def _inventory(p) -> str:
    return f"Inventory\n- Healing potions: {p['potions']}\n- Gold: {p['gold']}\n- Mana: {p['mana']}/{p['max_mana']}"

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
                "BARD - magical support; Dissonant Note, Inspiring Song at level 3\n\n Reply with WARRIOR, MAGE, ROGUE, PALADIN, RANGER, CLERIC, WARLOCK or BARD." 

    if p["status"] == "awaiting_class":
        chosen = upper
        if chosen not in CLASSES:
            return "Please choose WARRIOR, MAGE, ROGUE, PALADIN, RANGER, CLERIC, WARLOCK or BARD."
        stats = CLASSES[chosen]
        conn.execute("UPDATE players SET class=?, status='playing', hp=?, max_hp=?, mana=?, max_mana=?, location='Whistling Woods' WHERE email=?",
                     (chosen, stats["hp"], stats["hp"], stats["mana"], stats["mana"], email))
        return (f"Your adventure begins, {p['name']} the {chosen.title()}!\n\n"
                f"You are {stats['description']}. You have {stats['hp']} HP, {stats['mana']} mana and 2 healing potions.\n\n"
                "You stand at the edge of the Whistling Woods. What do you want to do?\n"
                "Reply EXPLORE to begin. Email ABILITIES to see your powers. MAP, STATUS, INVENTORY, ABILITIES and HELP are always free.\n\n" + _help())

    if upper in FREE_COMMANDS:
        if upper == "HELP":
            return _help()
        if upper in {"ABILITIES", "SPELLS"}:
            return _abilities(p)
        if upper == "STATUS":
            return _status(p)
        if upper == "MAP" or upper == "LOCATIONS":
            return _map(p)
        return _inventory(p)

    ability_name = upper[5:].strip() if upper.startswith("CAST ") else (upper[7:].strip() if upper.startswith("ABILITY ") else None)
    travel_destination = None
    if upper.startswith("TRAVEL "):
        requested_destination = upper[len("TRAVEL "):].strip().replace("'", "'")
        travel_destination = LOCATION_ALIASES.get(requested_destination)
        if travel_destination is None:
            return "I couldn't identify that destination. Email MAP for the list of locations. No daily action was used."
    elif upper == "TRAVEL":
        return "Where would you like to travel? Reply TRAVEL followed by a destination, such as TRAVEL HAUNTED RUINS. Email MAP for destinations. No daily action was used."

    if upper not in ACTIONS and travel_destination is None and ability_name is None:
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

# Check whether command is valid in the current context before spending the daily limit.
    if upper in {"ATTACK", "DEFEND", "POTION", "FLEE"} or ability_name) and not p["enemy_name"]:
        return "There is no Enemy here right now. Reply EXPLORE to look for one! No daily action was used."
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
    elif upper == "ATTACK" or ability_name:
        base = CLASSES[p["class"]]["attack"] + p["level"] - 1
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
            damage_taken = random.randint(1, max(2, p["enemy_attack"]))
            new_hp = max(0, current_hp - damage_taken)
            conn.execute("UPDATE players SET enemy_hp=?, hp=? WHERE email=?", (enemy_hp, new_hp, email))
            result.append(f"The {p['enemy_name']} hits back for {damage_taken} damage. You have {new_hp}/{p['max_hp']} HP left.")
            if new_hp == 0:
                conn.execute("UPDATE players SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Luminos' WHERE email=?", (max(1, p["max_hp"] // 2), email))
                result.append("You collapse and are carried back to town. You recover half health and lose 3 gold, but your adventure... continues.")
    elif upper == "DEFEND":
        damage_taken = max(1, random.randint(1, max(2, p["enemy_attack"])) // 2)
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
