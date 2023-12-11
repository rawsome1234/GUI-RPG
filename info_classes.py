from entities import *

class ShopItem():
    """ An item that can appear in a shop """
    def __init__(self, price):
        self.price = price

class Weapon(ShopItem):
    """ A storage mechanism for weapons and their information
    """

    def __init__(self, name, damage, elemental_damage, elemental_type, rarity, location, price=0):
        """ The constructer for the weapon class
    
            Inputs:
                name: the name of the weapon. This will be the display name as well as the reference name
                damage: the amount of damage the weapon will do. Subject to defense
                elemental_damage: the amount of elemental damage the weapon will do. Not subject to defense
                elemental_type: the type of elemental damage the weapon will do. A string that allows anything
                rarity: the chance for the weapon to appear
                location: where the weapon will appear. A string that represents an area ID or 'shops'
        """
        super().__init__(price)
        self.name = name
        self.damage = damage
        self.elemental_damage = elemental_damage
        self.elemental_type = elemental_type
        self.rarity = rarity
        self.location = location

    def __repr__(self):
        return f"A {self.rarity} {self.name}, which does {self.damage} damage with {self.elemental_damage} {self.elemental_type}"
    
    def copy(self):
        return Weapon(self.name, self.damage, self.elemental_damage, self.elemental_type, self.rarity, self.location, self.price)

# --------------------------------------------------------------------------------------

class Area():

    def __init__(self, name, tier, area_id, encounter_amount, shop_multiplier):
        """ A constructor for an area

            Inputs:
                name: the name of the area. Not displayed
                tier: the tier of area the area is
                area_id: the numerical id for the area. Must be unique
                encounter_amount: the number of encounters in this area
                shop_multiplier: the multiplier for the shop while the player is in the area
        """
        self.name = name
        self.tier = tier
        self.area_id = area_id
        self.encounters = encounter_amount
        self.shop_multiplier = shop_multiplier
        self.enemies = []
        self.weapons = []

    def get_inflation(self):
        return self.shop_multiplier

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def add_weapon(self, weapon: Weapon):
        self.weapons.append(weapon)

    def __repr__(self):
        return f"A tier {self.tier} {self.name}"

# --------------------------------------------------------------------------------------

class SpecialItem(ShopItem):
    """ Items that can modify stats about the player. They can only appear in shops. """

    
    def __init__(self, name, mod_type, mod_amount, price):
        """ The constructor for special items.
            Inputs:
                name: the name of the item
                mod_type: the stat being modified
                mod_amount: the amount the stat is being modified
        """
        super().__init__(price)
        self.name = name
        self.modifier_type = mod_type
        self.modifier_amount = mod_amount

    def apply_to_player(self, player: PlayerHandler):
        match self.modifier_type:
            case "health":
                player.base_health += self.modifier_amount
            case "defense":
                player.base_defense += self.modifier_amount
            case "critical damage":
                player.critical_multiplier += self.modifier_amount
            case "accuracy":
                player.miss_chance -= self.modifier_amount
            case "critical chance":
                player.critical_chance += self.modifier_amount
            case "minimum defense":
                if player.defenseLower == player.defenseUpper:
                    player.defenseUpper += self.modifier_amount
                else:
                    player.defenseLower += self.modifier_amount
            case "maximum defense":
                player.defenseUpper += self.modifier_amount
