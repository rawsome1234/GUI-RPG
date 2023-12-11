import json
from info_classes import *
from entities import *

weapons_location = "weapons.json"
areas_location = "areas.json"
enemies_location = "enemies.json"
special_items_location = "shop_items.json"

weapons = []
areas = []
enemies = []
shop_items = []
random_weapons = []
special_items = []

def parse_weapons():
    global weapons
    with open(weapons_location) as weapon_file:
        info = json.load(weapon_file)
        for weapon_key in info.keys():
            # the name of the weapon and it's dict reference are the same
            weapon_name = weapon_key

            # all the stats of the weapon
            weapon_info = info[weapon_key]

            # the weapon's stats are loaded...
            weapon_damage = weapon_info["damage"]
            weapon_element = weapon_info["element"]
            weapon_element_damage = weapon_info["element_damage"]
            weapon_rarity = weapon_info["rarity"]
            weapon_location = weapon_info["location"]
            
            weapon_price = 0
            if "price" in weapon_info.keys():
                weapon_price = weapon_info["price"]

            # creates the weapon object
            weapon = Weapon(weapon_name, weapon_damage, weapon_element_damage, weapon_element, weapon_rarity, weapon_location, weapon_price)

            # adds it to the list of weapons
            weapons.append(weapon)

def parse_areas():
    global areas
    with open(areas_location) as area_file:
        info = json.load(area_file)
        for area_key in info.keys():
            # the name of the area and it's dict reference are the same
            area_name = area_key

            # all the stats of the area
            area_info = info[area_key]

            # the area's information is loaded...
            area_tier = area_info["tier"]
            area_id = area_info["id"]
            area_encounters = area_info["encounters"]
            area_multiplier = area_info["shop_multiplier"]

            # creates the area object
            area = Area(area_name, area_tier, area_id, area_encounters, area_multiplier)

            # adds it to the list of area
            areas.append(area)

def parse_special_items():
    global special_items
    with open(special_items_location) as shop_file:
        info = json.load(shop_file)
        for item_key in info.keys():
            # the name of the item and it's dict reference are the same
            item_name = item_key

            # all the modifier information for the special information
            item_info = info[item_key]

            # poor naming but it works haha
            item_type = item_info["modifier"]
            item_modifier = item_info["amount"]
            price = item_info["price"]

            # creates the item object
            special_item = SpecialItem(item_name, item_type, item_modifier, price)

            # adds it to the list of shop items
            special_items.append(special_item)

def parse_enemies():
    global enemies
    with open(enemies_location) as enemy_file:
        info = json.load(enemy_file)
        for enemy_key in info.keys():
            # the name of the enemy and it's dict reference are the same
            enemy_name = enemy_key

            # all the stats of the enemy
            enemy_info = info[enemy_key]

            # the enemy's information is loaded...
            enemy_damage = enemy_info["damage"]
            enemy_element = enemy_info["element"]
            enemy_element_damage = enemy_info["element_damage"]
            enemy_health = enemy_info["health"]
            enemy_defense = enemy_info["defense"]
            enemy_attack_chance = enemy_info["attack_chance"]
            enemy_defense_chance = enemy_info["defense_chance"]
            enemy_coins = enemy_info["coins_dropped"]

            # creates the area object
            enemy = Enemy(enemy_name, enemy_damage, enemy_element, enemy_element_damage, enemy_health, + \
                          enemy_defense, enemy_attack_chance, enemy_defense_chance, enemy_coins)

            # adds it to the list of area
            enemies.append(enemy)

def validate_areas_and_locations():
    # making sure no two areas share an id
    ids = []
    for area in areas:
        area_id = area.area_id
        if area_id in ids:
            print("Duplicate area ID of id " + str(area_id))
            return False
        ids.append(area_id)

    # sorting enemies into areas
    # copy enemy list
    enemy_list = enemies.copy()
    # print(f"Enemy List is {len(enemy_list)}")
    
    # sorting..
    with open(enemies_location) as enemy_file:
        info = json.load(enemy_file)
        for enemy in enemy_list:
            location_id = info[enemy.name]["location_id"]
            if type(location_id) == type(["a"]):
                for location in location_id:
                    assign_enemy_to_location(enemy, location)
            elif location_id != None:
                assign_enemy_to_location(enemy, location_id)
            else:
                continue
        
    # sorting weapons into areas
    # copy weapon list
    weapon_list = weapons.copy()


    # sorting..
    with open(weapons_location) as weapon_file:
        info = json.load(weapon_file)
        for weapon in weapon_list:
            location_id = info[weapon.name]["location"]
            # print(location_id)
            if type(location_id) == type(["a"]):
                for location in location_id:
                    assign_weapon_to_location(weapon, location)
            elif location_id != None:
                assign_weapon_to_location(weapon, location_id)
            else:
                continue

def assign_enemy_to_location(enemy: Enemy, location_id):
    global areas
    for area in areas:
        if area.area_id == location_id:
            area.add_enemy(enemy)

def assign_weapon_to_location(weapon: Weapon, location_id):
    global shop_items
    global random_weapons
    global areas
    # for the shop
    if location_id == "shop":
        shop_items.append(weapon)
        return
    
    # can appear anywhere
    elif location_id == "random":
        random_weapons.append(weapon)
        return
    
    # print(weapon.name)

    # assign the weapon to an area
    for area in areas:
        if area.area_id == location_id:
            area.add_weapon(weapon)

def get_areas_of_tier(tier):
    assert(type(tier) == type(1))
    ret = []
    for a in areas:
        if a.tier == tier:
            ret.append(a)
    return ret

def parse_info():
    parse_weapons()
    parse_areas()
    parse_enemies()
    parse_special_items()
    # print(f"Weapon count: {len(weapons)}")
    validate_areas_and_locations()