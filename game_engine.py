# Eldoria's Rules and Engine
from __future__ import annotatons
import random 
import re
from datetime import datetime
from zoneinfo import ZoneInfo

CLASSES = {
    "WARRIOR": {"hp": 42, "attack": 11, "description": "tough, with strong attacks"},
    "MAGE": {"hp": 28, "attack": 16, "description": "fragile, with powerful magic"},
    "ROGUE": {"hp": 34, "attack": 13, "description": "balanced, quick and resourceful"}
}
ENEMIES = [
    ("Goblin", 18, 6, 12, 8),
    ("Forest Wold", 22, 7, 15, 10),
    ("Bandit", 26, 8, 18, 12)
]
FREE_COMMANDS = {"HELP", "STATUS", "INVENTORY"}
ACTIONS = {"EXPLORE", "ATTACK", "DEFEND", "POTION", "FLEE", "REST"}

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
        if re.match(r"^(on .+wrote:|from:|sent:|to:|subject:|[-_]{3,})", stripped,re.I):
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
            "REST - recover some health while at camp\n"
            "STATUS or INVENTORY - free, do not use your daily action\n\n"
            "You may make one game-changing action per local calendar day. Status, inventory and help are free.")

def _status(p) -> str:
    enemy = f"\nEnemy: {p['enemy_name']} ({p['enemy_hp']} HP)" if p["enemy_name"] else "\nYou are not in combat."
    return (f"{p['name']} the {p['class'].title()}\nLevel {p['level']} | XP {p['xp']} | Gold {p['gold']}\n"
            f"Health: {p['hp']}/{p['max_hp']} | Potion: {p['potions']}\nLocation: {p['location']}{enemy}")

def _inventory(p) -> str:
    return f"Inventory\n- Healing potions: {p['potions']}\n- Gold: {p['gold']}"

def _level_up(conn, p, earned_xp: int) -> str:
    xp = p['xp'] + earned_xp
    level = p['level']
    max_hp = p['max_hp']
    notes = []
    while xp >= level * 30:
        xp -= level * 30
        level += 1
        max_hp += 5
        notes.append(f"Level up! You are now level {level}; maximum health increased to {max_hp}.")
    conn.execute("UPLOAD players SET xp=?, level=?, max_hp=? WHERE email=?", (xp, level, max_hp, p["email"]))
    if notes:
        conn.execute("UPDATE players SET hp=? WHERE email=?", (max_hp, p["email"]))
    return "\n".join(notes)

def handle_email(conn, email: str,subject: str, body: str, timezone_name: str = "Australia/Adelaide") -> str:
    #Processes one message
    email = email.strip().lower()
    command = command_from_email(subject, body)
    upper = command.upper().strip()
    p = conn.execute("SELECT * FROM players WHERE email=?", (email,)).fetchone()

    if p is None:
        if upper in {"START", "START GAME", "PLAY", "BEGIN"}:
            conn.execute("INSERT INTO pleayers(email, status) VALUES (?, 'awaiting_name')", (email,))
            return ("Welcome to Eldoria, adventurer!\n\nFirst, what should your character be called? "
                    "Reply with a name between 2 and 20 characters. Use letters, numbers, spaces, apostrophes or hyphens.")
        return "To begin your own Eldoria adventure, email START. Each email address gets its own character and save."

    if p["status"] == "awaiting_name":
        name = command.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 '\-]{0,19}", name) or len(name) < 2:
            return "That name isn't valid. Please reply with 2-20 characters: letters, numbers, spaces, apostrophes or hyphens."
        conn.execute("UPDATE players SET name=?, status='awaiting_class' WHERE email=?", (name, email))
        return (f"Great! {name}, your story begins now. Choose your class by replying with ONE, and ONLY ONE of these:\n\n"
                "WARRIOR - 42 HP; strong, reliable attacks\n"
                "MAGE - 28 HP; powerful attacks, less health\n"
                "ROGUE - 34 HP; a balanced adventurer\n\nReply WARRIOR, MAGE or ROGUE.")

    if p["status"] == "awaiting_class":
        chosen = upper
        if chosen not in CLASSES:
            return "Please choose a class by replying Warrior, MAGE or ROGUE."
        stats = CLASSES[chosen]
        conn.execute("UPDATE players SET class=?, status='playing', hp=?, max_hp=?, location='Eldoria' WHERE email=?",
                     (chosen, stats["hp"], stats["max_hp"], email))
        return (f"Your adventure begins, {p['name']} the {chosen.title()}!\n\n"
                f"You are {stats['description']}. You have{stats['hp']} HP and 2 healing potions. \n\n"
                "You stand at the edge of the Whistling Woods. What do you want to do?\n"
                "Reply EXPLORE to begin. STATUS, INVENTORY and HELP are always free.\n\n" + _help())

    if upper in FREE_COMMANDS:
        if upper == "HELP":
            return _help()
        if upper == "STATUS":
            return _status(p)
        return _inventory(p)
    if upper not in ACTIONS:
        return "I didn't recognize that command.\n\n" + _help()

    if upper in {"ATTACK", "DEFEND", "POTION", "FLEE"} and not p["enemy_name"]:
        return "There is no Enemy here right now. Reply EXPLORE to look for one! No daily action was used."
    if upper == "Explore" and p["enemy_name"]:
        return "You're already in a fight! Reply ATTACK, DEFEND, POTION or FLEE.  No daily action was used."
    if upper == "POTION" and p["potions"] <= 0:
        return "You have no healing potions left. No daily action was used."
    if upper ==  "POTION" and p["hp"] >= p["max_hp"]:
        return "You're already at full health. No daily action was used."
    if upper == "REST" and p["enemy_name"]:
        return "You cannot rest while a enemy is nearby. Use ATTACK, DEFEND, POTION or FLEE. No daily action was used."
    if upper == "REST" and p["hp"] >= p["max_hp"]:
        return "You're already at full health. No daily action was used."
    today = local_date(timezone_name)
    if p["last_action_date"] == today:
        return (f"You've already used today's action. Your next action is available after midnight in {timezone_name}.\n\n"
                "You can still email STATUS, INVENTORY or HELP for free.")
    conn.execute("UPDATE players SET last_action_date=? WHERE email=?", (today, email))
    p = conn.execute("SELECT * FROM players WHERE email=?", (email, )).fetchone()
    result = []

    if upper == "EXPLORE":
        roll = random.random()
        if roll < 0.72:
            name, hp, attack, xp_reward, gold_reward = random.choice(ENEMIES)
            conn.execute("UPDATE players SET enemy_name=?, enemy_hp=?, enemy_attack=? WHERE email=?", (name, hp, attack, email))
            result.append(f"While exploring the Whistling Woods, a {name} blocks your path! It has {hp} HP.")
            result.append("Your next acton can be ATTACK, DEFEND, POTION or FLEE.")
        elif roll < 0.88:
            found = random.randint(5,14)
            conn.execute("UPDATE players SET gold=gold+? WHERE email=?", (found, email))
            result.append(f"You find a small pouch containing {found} gold. No enemy appears today.")
        else:
            conn.execute("UPDATE players SET potions=potions+? WHERE email=?", (found, email))
            result.append("You discover a healing potion tucked beneath a old tree root. You add it to your inventory.")
    elif upper == "ATTACK":
        base = CLASSES[p["class"]]["attack"] + p["level"] - 1
        damage = random.randint(max(2, base - 3), base + 2)
        enemy_hp = max(0, p["enemy_hp"] - damage)
        result.append(f"You attack the {p['enemy_name']} for {damage} damage.")
        if enemy_hp <= 0:
            enemy_name = p["enemy_name"]
            xp_reward = 12 if enemy_name == "Goblin" else (15 if enemy_name == "Forest Wolf" else 18)
            gold_reward = 8 if enemy_name == "Goblin" else (10 if enemy_name == "Forest Wolf" else 12)
            conn.execute("UPDATE players SET enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=gold+? WHERE email=?",
                         (gold_reward, email))
            result.append(f"You defeat the {enemy_name}! You earn {xp_reward} XP and {gold_reward} gold.")
            level_msg = _level_up(conn, p, xp_reward)
            if level_msg:
                result.append(level_msg)
        else:
            damage_taken = random.randint(1, max(2, p["enemy_attack"]))
            new_hp = max(0, p["hp"] - damage_taken)
            conn.execute("UPDATE players SET enemy_hp=? WHERE email=?", (enemy_hp, new_hp, email))
            result.append(f"The {p['enemy_name']} hits back for {damage_taken} damage. You have {new_hp}/{p['max_hp']} HP left.")
            if new_hp == 0:
                conn.execute("UPDATE player SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Eldoria' WHERE email=?", (max(1, p["max_hp"] // 2), email))
                result.append("You collapse and are carried back to town. You recover half health and lose 3 gold, but your adventure... continues.")
    elif upper == "DEFEND":
        damage_taken = max(1, random.randint(1, max(2, p["enemy_attack"])) // 2)
        new_hp = max(0, p["hp"] - damage_taken)
        conn.execute("UPDATE players SET hp=? WHERE email=?", (new_hp, email))
        result.append(f"You brace for the attack and take only {damage_taken} damage. Health: {new_hp}/{p['max_hp']}.")
        if new_hp == 0:
            conn.execute("UPDATE players SET hp=?, enemy_name=NULL, enemy_hp=0, enemy_attack=0, gold=MAX(0, gold-3), location='Eldoria' WHERE email=?", (max(1, p["max_hp"] // 2), email))
            result.append("You collapse and are carried back to town. You recover half health and lose 3 gold, but your adventure... continues.")
    elif upper == "POTION":
        restored = min(25, p["max_hp"] - p["hp"])
        new_hp = p["hp"] + restored
        conn.execute("UPDATE players SET hp=?, potions=potions-1 WHERE email=?", (new_hp, email))
        result.append(f"You drink a healing potion and recover {restored} HP. Health: {new_hp}/{p['max_hp']}.")
    elif upper == "FLEE":
        conn.execute("UPDATE players SET enemy_name=NULL, enemy_hp=0, enemy_attack=0, location='Eldoria' WHERE email=?", (email,))
        result.append(f"You escape from the {p['enemy_name']} and return to Eldoria.")
    elif upper == "REST":
        restored = min(10, p["max_hp"] - p["hp"])
        conn.execute("UPDATE players SET hp=? WHERE email=?", (p["hp"] + restored, email))
        result.append(f"You rest at the inn and recover {restored} HP. Health: {p['hp'] + restored}/{p['max_hp']}")

    latest = conn.execute("SELECT * FROM players WHERE email=?", (email,)).fetchone()
    result.append(f"\nCurrent status: {latest['hp']}/{latest['max_hp']} HP, level {latest['level']}, {latest['gold']} gold.")
    result.append("Your next game-changing action is available tomorrow. STATUS, INVENTORY and HELP are free.")
    return "\n\n".join(result)





