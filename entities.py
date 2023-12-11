import random
from pygame_class_handlers import *
from info_classes import *
from packets import *

class Enemy():
    """ The data for an enemy - SHOULD NOT BE MODIFIED AFTER CREATION """

    def __init__(self, name, damage, elemental_type, elemental_damage, health, defense, attack_chance, defense_chance, coins):
        """ The constructor for the information in the enemy class

            Inputs:
                name: the display name for the enemy
                damage: the amount of damage the weapon will do. Subject to defense
                elemental_damage: the amount of elemental damage the weapon will do. Not subject to defense
                elemental_type: the type of elemental damage the weapon will do. A string that allows anything
                health: the amount of health the enemy starts with
                defense: the amount of defense the enemy starts with
                attack_chance: the weight for the enemy to attack
                defense_chance: the weight for the enemy to defense
                coins: the number of coins the enemy will drop upon defeat
        """
        self.name = name
        self.damage = damage
        self.elemental_type = elemental_type
        self.elemental_damage = elemental_damage
        self.health = health
        self.defense = defense
        self.attack_chance = attack_chance
        self.defense_chance = defense_chance
        self.coins_dropped = coins

class LivingEntity():
    """ An entity in the game that has health, and can be hurt """

    def __init__(self) -> None:
        """ constructor for the LivingEntity class. Initializes a bunch of variables"""
        self.elemental_damage_turns = 0
        self.elemental_damage_type = ""
        self.elemental_damage_amount = 0
        self.health = 10
        self.defense = 0
        self.defenseLower = 1
        self.defenseUpper = 3
        self.critical_chance = 0.1
        self.critical_multiplier = 1.5
        self.miss_chance = .025
        self.miss_elemental_multiplier = 2
        self.name = None

    def damage(self, amount, elemental=False, elemental_amount=0, elemental_type="none"):
        """ Called when this entity is receiving damage 
        
            amount: the amount of damage being dealt
            elemental: if the damage is elemental or regular. defaults to false (regular damage)
            elemental_amount: the amount of elemental daamge being inflicted per turn. Defaults to 0
            elemental_type: the type of elemental damage inflicted. Defaults to 'none'
        """
        if not elemental:
            amount -= self.defense
        elemental_output = False
        if not elemental and elemental_type != "none":
            elemental_output = self.inflict_elemental_damage(elemental_type, elemental_amount)

        if amount > 0:
            self.health -= amount
            return AttackPacket(amount, elemental, elemental_type, self, None, elemental_output)
            
        return AttackPacket(0, elemental, elemental_type, self, None, elemental_output)
    
    def increase_defense(self):
        """ increases the defense of this entity by a random number between defenseLower and defenseUpper """
        increase = random.randint(self.defenseLower, self.defenseUpper)
        self.defense += increase
        packet = DefensePacket(self, self.defense, increase)
        return packet
    
    def take_turn(self, target=None):
        """ An empty method for inheritence. Should be used to decid what turn to take """
        pass

    def inflict_elemental_damage(self, elemental_type, damage_amount):
        """ start taking elemental damage if not already 
        
            elemental_type: the type of elemental damage being taken
            damage_amount: the amount of damage being taken
        """
        if self.elemental_damage_turns == 0:
            self.elemental_damage_turns = random.randint(2,3)
            self.elemental_damage_type = elemental_type
            self.elemental_damage_amount = damage_amount
            return True
        return False
    
    def take_elemental_damage(self):
        """ called every turn for this entity to take elemental damage """
        if self.elemental_damage_turns > 0:
            self.elemental_damage_turns -= 1
            packet = self.damage(self.elemental_damage_amount, True)
            packet.elemental_type = self.elemental_damage_type
            return packet
        return False
    
    def end_elemental(self):
        """ if the number of elemental turns left is 0, it will clear its information """
        if self.elemental_damage_turns == 0:
            self.elemental_damage_amount = 0
            self.elemental_damage_type = "none"
            return True
        return False
    
    def is_alive(self):
        """ returns true if this entity has more than 0 health """
        return self.health > 0
    
    def heal(self, amount):
        pass

    def attack_other(self, target):
        """ Makes this living entity attack another living entity 
        
            target: the other living entity to be attacked
        """
        # roll for a critical
        crit = random.randint(1,(int(1/self.critical_chance)))
        damage = self.get_damage()
        if crit == 1:
            damage *= self.critical_multiplier
            damage = int(damage)

        # check for a miss - Criticals override misses
        miss = self.accuracy_check()
        if miss and not crit == 1:
            return AttackPacket(0, False, "", target, self, False, False, True)
        
        # deal damage and get the packet response
        packet: AttackPacket = target.damage(damage, False, self.get_elemental_damage(), self.get_elemental_type())

        # some information needed in the packet
        packet.target = target
        packet.executer = self
        packet.critical = crit == 1
        packet.elemental_type = self.get_elemental_type()
        return packet
    
    def accuracy_check(self):
        miss_chance = self.miss_chance
        if self.is_taking_elemental_damage():
            miss_chance *= self.miss_elemental_multiplier
        return random.randint(1, (int(1/miss_chance))) == 1

    def is_taking_elemental_damage(self):
        return self.elemental_damage_turns > 0

    def get_name(self):
        return self.name
    
    def format_name(self):
        return self.name[0].upper() + self.name[1:]

    def get_damage(self):
        return 0
    
    def get_elemental_damage(self):
        return 0
    
    def get_elemental_type(self):
        return "none"


class EnemyInstance(LivingEntity):
    """ An instance of an enemy the player will fight.
    """

    def __init__(self, enemy_info: Enemy):
        """ The constructor for the EnemyInstance class

            Inputs:
                enemy_info: the enemy information this instance is based on.
        """
        super().__init__()
        self.enemy_info = enemy_info
        self.health = enemy_info.health
        self.defense = enemy_info.defense
        self.name = enemy_info.name

    def decide_turn(self):
        total = self.enemy_info.defense_chance + self.enemy_info.attack_chance
        rand = random.randint(1, total)
        if rand <= self.enemy_info.attack_chance:
            return "attack"
        else:
            return "defend"


    def take_turn(self, target: LivingEntity=None):
        if self.decide_turn() == "attack":
            return self.attack_other(target)
        else:
            return self.increase_defense()
        
    def get_damage(self):
        return self.enemy_info.damage
    
    def get_elemental_damage(self):
        return self.enemy_info.elemental_damage
    
    def get_elemental_type(self):
        return self.enemy_info.elemental_type
            




class PlayerHandler(LivingEntity):
    """ A class that stores information about a player object """

    def __init__(self):
        super().__init__()
        self.base_health = 20
        self.health = self.base_health
        self.base_defense = 0
        self.defense = self.base_defense
        self.coins = 0
        self.potions = 0
        self.weapon = []
        self.name = "you"
        self.weapon_options = []

    def get_damage(self):
        return self.weapon.damage
    
    def get_elemental_damage(self):
        return self.weapon.elemental_damage
    
    def get_elemental_type(self):
        return self.weapon.elemental_type
    
    def can_purchase_weapon(self, weapon, inflation):
        res = (int(weapon.price * inflation) <= self.coins)
        # print(res)
        return res

    def purchase_item(self, weapon, inflation):
        self.coins -= int(weapon.price * inflation)
        self.weapon_options.append(weapon)

    def rest(self):
        self.health = self.base_health
        self.defense = self.base_defense
        self.elemental_damage_turns = 0
        self.end_elemental()

    def heal(self, amount):
        if self.health + amount > self.base_health:
            amount = self.base_health - self.health
        self.health += amount
        max = False
        if self.health >= self.base_health:
            self.health = self.base_health
            self.elemental_damage_turns = 0
            self.end_elemental()
            max = True
        return HealthPacket(self, amount, max)