import sqlite3
import unittest
from unittest.mock import patch

from database import SCHEMA
from game_engine import ABILITIES, CLASSES, ENEMIES, ENEMY_MIN_LEVEL, LOCATION, handle_email


class GameEngineTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
    
    def tearDown(self):
        self.conn.close()

    def send(self, email, text, subject='Re: Luminos'):
        return handle_email(self.conn, email, subject, text, 'Australia/Adelaide')

    def create_player(self, email, name, player_class):
        self.send(email, 'START', 'START')
        self.send(email, name)
        self.send(email, player_class)

    def test_character_creation_by_email(self):
        self.assertIn('what should your character be called', self.send('a@example.com', 'START', 'START'))
        self.assertIn('Choose your class', self.send('a@example.com', 'Aria'))
        self.assertIn('adventure begins', self.send('a@example.com', 'MAGE'))
        player = self.conn.execute('SELECT * FROM players WHERE email=?', ('a@example.com',)).fetchone()
        self.assertEqual((player['name'], player['class'], player['status'], player['hp']), ('Aria', 'MAGE', 'playing', 28))
        self.assertIsNone(player['last_action_date'])

    def test_each_email_has_independent_save_and_turn(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        self.create_player('b@example.com', 'Borin', 'WARRIOR')
        with patch('game_engine.random.random', return_value=0.99):
            self.send('a@example.com', 'EXPLORE')
        blocked = self.send('a@example.com', 'EXPLORE')
        self.assertIn("already used today's action", blocked)
        with patch('game_engine.random.random', return_value=0.99):
            other = self.send('b@example.com', 'EXPLORE')
        self.assertNotIn("already used today's action", other)

    def test_status_is_free_after_action(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        with patch('game_engine.random.random', return_value=0.99):
            self.send('a@example.com', 'EXPLORE')
        status = self.send('a@example.com', 'STATUS')
        self.assertIn('Aria the Mage', status)
        self.assertNotIn("already used today's action", status)

    def test_enemy_roster_has_multiple_level_tiers(self):
        self.assertGreaterEqual(len(ENEMIES), 10)
        self.assertEqual(ENEMY_MIN_LEVEL["Goblin"], 1)
        self.assertEqual(ENEMY_MIN_LEVEL["Young Dragon"], 9)

    def test_level_one_exploration_cannot_spawn_high_level_enemy(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        #Force a encounter, then let game choose from pool of enemies
        with patch('game_engine.random.random', return_value=0.0), \
            patch('game_engine.random.choice', side_effect=lambda enemies: enemies[-1]):
            reply = self.send('a@example.com', 'EXPLORE')
        self.assertIn('Bandit', reply)
        self.assertNotIn('Young Dragon', reply)

    def test_map_lists_locations_and_level_requirements_for_free(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        response = self.send('a@example.com', 'MAP')
        self.assertIn('Whistling Woods', response)
        self.assertIn('Goblin Cave', response)
        self.assertIn("Dragon's Lair", response)
        player = self.conn.exectute('SELECT last_action_date FROM players WHERE email=?', ('a@example.com',)).fetchone()
        self.assertIsNone(player['last_action_date'])

    def test_locked_location_does_not_consume_daily_action(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        response = self.send("a@example.com", "TRAVEL DRAGON's LAIR")
        self.assertIn('need to reach level 9', response)
        player = self.conn.execute('SELECT last_action_date, location FROM players WHERE email=?', ('a@example.com',)).fetchone()
        self.assertIsNone(player['last_action_date'])
        self.assertEqual(player['location'], 'Whistling Woods')

    def test_travel_changes_location_and_uses_daily_action(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        self.conn.execute("UPDATE players SET level=2 WHERE email='a@example.com'")
        response = self.send('a@example.com', 'TRAVEL GOBLIN CAVES')
        self.assertIn('You travel to Goblin Caves', response)
        player = self.conn.execute('SELECT location, last_action_date FROM players WHERE email=?', ('a@example.com',)).fetchone()
        self.assertEqual(player['location'], 'Goblin Caves')
        self.assertIsNotNone(player['last_action_date'])
        blocked = self.send('a@example.com', 'TRAVEL WHISTLING WOODS')
        self.assertIn("already used today's action", blocked)

    def test_each_location_has_its_own_encounter_pool(self):
        self.assertNotEqual(LOCATIONS['Whistling Woods']['enemies'], LOCATIONS['Goblin Caves']['enemies'])
        self.assertIn('Young Dragon', LOCATIONS["Dragon's Lair"]['enemies'])
        self.assertEqual(LOCATIONS['Luminos']['enemies'], ())

    def test_level_one_cannot_explore_safe_town(self):
        self.create_player('a@example.com', 'Aria', 'MAGE')
        self.conn.execute("UPDATE players SET location='Luminos' WHERE email='a@example.com'")
        response = self.send('a@example.com', 'EXPLORE')
        self.assertIn('safe town', response)
        player = self.conn.execute('SELECT last_action_date FROM players WHERE email=?', ('a@example.com', )).fetchone()
        self.assertIsNone(player['last_action_date'])

    def test_all_eight_classes_can_be_created(self):
        self.assertEqual(len(CLASSES), 8)
        self.assertIn("SHIELD BASH", ABILITIES)
        self.assertIn("POISON BLADE", ABILITIES)
        for index, player_class in enumerate(CLASSES):
            email = f"class{index}@example.com"
            self.create_player(email, f"Hero{index}", player_class)
            player = self.conn.execute("SELECT class, mana, max_mana FROM players WHERE email=?", (email,)).fetchone()
            self.assertEqual(player["class"], player_class)
            self.assertEqual(player["mana"], player["max_mana"])
            self.assertGreater(player["max_mana"], 0)
    
    def test_abilities_command_is_free_and_class_specific(self):
        self.create_player("mage@example.com", "Aria", "MAGE")
        response = self.send("mage@example.com", "ABILITIES")
        self.assertIn("FIREBALL", response)
        self.assertIn("ICE SHARD", response)
        self.assertNotIn("BACKSTAB", response)
        player = self.conn.execute("SELECT last_action_date FROM players WHERE email='mage@example.com'").fetchone()
        self.assertIsNone(player["last_action_date"])

    def test_cast_ability_spends_mana_and_daily_action(self):
        self.create_player("mage@example.com", "Aria", "MAGE")
        self.conn.execute("UPDATE players SET enemy_name='Goblin', enemy_hp=100, enemy_attack=1 WHERE email='mage@example.com'")
        response = self.send("mage@example.com", "CAST FIREBALL")
        player = self.conn.execute("SELECT mana, enemy_hp, last_action_date FROM player WHERE email='mage@example.com'").fetchone()
        self.assertIn("Fireball", response)
        self.assertEqual(player["mana"], 8)
        self.assertLess(player["enemy_hp"], 100)
        self.assertIsNotNone(player["last_action_date"])
        self.assertIn("already used today's action", self.send("mage@example.com", "CAST FIREBALL"))

    def test_wrong_class_ability_does_not_use_daily_action(self):
        self.create_player("warrior@example.com", "Borin", "WARRIOR")
        self.conn.execute("UPDATE players SET enemy_name='Goblin', enemy_hp=100, enemy_attack=1 WHERE email='warrior@example.com'")
        response = self.send("warrior@example.com", "CAST FIREBALL")
        player = self.conn.execute("SELECT last_action_date, mana FROM players WHERE email='warrior@example.com'").fetchone()
        self.assertIn("Only a Mage", response)
        self.assertIsNone(player["last_action_date"])
        self.assertEqual(player["mana"], CLASSES["WARRIOR"]["mana"])

    def test_rest_restores_mana_even_at_full_health(self):
        self.create_player("mage@example.com", "Aria", "MAGE")
        self.conn.execute("UPDATE players SET mana=1 WHERE email='mage@example.com'")
        response = self.send("mage@example.com", "REST")
        player = self.conn.execute("SELECT mana, max_mana FROM players WHERE email='mage@example.com'").fetchone()
        self.assertIn("recover 0 HP and 11 mana", response)
        self.assertEqual(player["mana"], player["max_mana"])

    def test_invalid_name_does_not_advance_creation(self):
        self.send('a@example.com', 'START', 'START')
        response = self.send('a@example.com', 'A')
        self.assertIn("isn't valid", response)
        player = self.conn.execute('SELECT status FROM players WHERE email=?', ('a@example.com',)).fetchone()
        self.assertEqual(player['status'], 'awaiting_name')

    def test_shop_is_free_and_only_available_in_luminos(self):
        self.create_player("shopper@example.com", "Mira", "WARRIOR")
        self.assertIn("market is in Luminos", self.send("shopper@example.com", "SHOP"))
        self.conn.execute("UPDATE players SET location='Luminos' WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "SHOP")
        self.assertIn("IRON SWORD", response.upper())
        player = self.conn.execute("SELECT last_action_date FROM players WHERE email='shopper@example.com'").fetchone()
        self.assertIsNone(player["last_action_date"])

    def test_buy_weapons_spends_gold_and_daily_action(self):
        self.create_player("shopper@example.com", "Mira", "WARRIOR")
        self.conn.execute("UPDATE players SET location='Luminos', gold=100 WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "BUY IRON SWORD")
        player = self.conn.execute("SELECT gold, weapon, attack_bonus, last_action_date FROM players WHERE email='shopper@example.com'").fetchone()
        self.assertIn("equip the Iron Sword", response)
        self.assertEqual((player["gold"], player["weapon"], player["attack_bonus"]), (45, "IRON SWORD", 4))
        self.assertIsNotNone(player["last_action_date"])

    def test_insufficient_gold_does_not_spend_daily_action(self):
        self.create_player("shopper@example.com", "Mira" "WARRIOR")
        self.conn.execute("UPDATE players SET location='Luminos', gold=1 WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com")
        self.assertIn("costs 55 gold", response)
        player = self.conn.execute("SELECT last_action_date, gold FROM players WHERE email='shopper@example.com'").fetchone()
        self.assertIsNone(player["last_action_date"])
        self.assertEqual(player["gold"], 1)

    def test_mana_potion_purchase_and_use(self):
        self.create_player("shopper@example.com", "Mira", "MAGE")
        self.conn.execute("UPDATE players SET location='Luminos', gold=100, mana=1 WHERE email='shopper@example.com'")
        self.send("shopper@example.com", "BUY MANA POTION")
        self.conn.execute("UPDATE players SET last_action_date='2000-01-01' WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "USE MANA POTION")
        player = self.conn.execute("SELECT mana FROM players WHERE email='shopper@example.com' AND item='MANA POTION'").fetchone()
        self.assertIn("restore 10 mana", response)
        self.assertEqual(player["mana"], 11)
        self.assertEqual(item["quantity"], 0)

    def test_bomb_is_consumed_and_cannot_be_reused_when_empty(self):
        self.create_player("bomb@example.com", "Kade", "ROGUE")
        self.conn.execute("INSERT INTO player_items(email,item,quantity) VALUES ('bomb@example.com', 'BOMB',1)")
        self.conn.execute("UPDATE players SET enemy_name='Goblin', enemy_hp=100, enemy_attack=1 WHERE email='bomb@example.com'")
        response = self.send("bomb@example.com", "USE BOMB")
        self.assertIn("dealing 20 damage", response)
        self.conn.execute("UPDATE players SET last_action_date='2000-01-01' WHERE email='bomb@example.com'")
        response = self.send("bomb@example.com", "USE BOMB")
        self.assertIn("don't have a bomb", response)

    def test_advanced_abilites_exist_for_all_classes(self):
        for player_class in CLASSES:
            class_abilities = [a for a in ABILITIES.values() if a["class"] == player_class]
            self.assertGreaterEqual(len(class_abilities), 4)
            self.assertTrue(any(a["level"] == 5 for a in class_abilities))
            self.assertTrue(any(a["level"] == 7 for a in class_abilities))

    def test_advanced_spell_unlocks_at_level_five(self):
        self.create_player("mage@example.com", "Aria", "MAGE")
        self.conn.execute("UPDATE players SET level=4, enemy_name='Goblin', enemy_hp=100, enemy_attack=1 WHERE email='mage@example.com'")
        response = self.send("mage@example.com", "CAST LIGHTNING BOLT")
        self.assertIn("unlocks at level 5", response)
        self.conn.execute("UPDATE players SET level=5 WHERE email='mage@example.com'")
        self.conn.execute("UPDATE players SET last_action_date='2000-01-01' WHERE email='mage@example.com'")
        response = self.send("mage@example.com", "CAST LIGHTNING BOLT")
        self.assertIn("Lightning Bolt", response)

    def test_shop_lists_new_items(self):
        self.create_player("shopper@example.com", "Mira", "WARRIOR")
        self.conn.execute("UPDATE players SET location='Luminos' WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "SHOP")
        for item in ("GREATER HEALING POTION", "GREATER MANA POTION", "ELIXIR OF VIGOUR", "FIRE SCROLL", "MITHRIL SWORD" "RUNED STAFF", "PLATE ARMOUR"):
            self.assertIn(item, response.upper())

    def test_greater_healing_potion_purchase_and_use(self):
        self.create_player("shopper@example.com", "Mira", "WARRIOR")
        self.conn.execute("UPDATE players SET location='Luminos', gold=100, hp=20 WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "BUY GREATER HEALING POTION")
        self.assertIn("greater healing potion", response.lower())
        self.conn.execute("UPDATE players SET last_action_date='2000-01-01' WHERE email='shopper@example.com'")
        response = self.send("shopper@example.com", "USE GREATER HEALING POTION")
        player = self.conn.execute("SELECT hp, max_hp FROM players WHERE email='shopper@example.com'").fetchone()
        item = self.conn.execute("SELECT quantity FROM player_items WHERE email='shopper@example.com' AND item='GREATER HEALING POTION'").fetchone()
        self.assertEqual(player["hp"], player["max_hp"])
        self.assertEqual(item["quantity"], 0)
    
    def test_fire_scroll_deals_damage_and_is_consumed(self):
        self.create_player("scroll@example.com", "Aria", "MAGE")
        self.conn.execute("INSERT INTO player_items(email,item,quantity) VALUES ('scroll@example.com','FIRE SCROLL',1)")
        self.conn.execute("UPDATE players SET enemy_name='Goblin', enemy_hp=100, enemy_attack=1 WHERE email='scroll@example.com'")
        response = self.send("scroll@example.com", "USE FIRE SCROLL")
        self.assertIn("dealing 35 damage", response)
        player = self.conn.execute("SELECT enemy_hp FROM players WHERE email='scroll@example.com'").fetchone()
        item = self.conn.execute("SELECT quantity FROM player_items WHERE email='scroll@example.com' AND item='FIRE SCROLL'").fetchone()
        self.assertEqual(player["enemy_hp"], 65)
        self.assertEqual(item["quantity"], 0)


if __name__ == '__main__':
    unittest.main()