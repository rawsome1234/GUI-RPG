class InformationPacket():
    """ A template for packets that should be inherited from """

    def __init__(self, type=None):
        self.type = type

class AttackPacket(InformationPacket):
    """ A Packet that holds information for attack actions"""

    def __init__(self, damage: int, elemental_damage: bool, elemental_type: str, target, executer, elemental_inflict: bool, critical=False, miss=False):
        """ Constructor for an attack packet
        
            damage: the amount of damage dealt by an attack
            elemental_damage: if the damage was elemental
            elemental_type: what element the damage was, if elemental
            target: a LivingEntity that was the target of the attack
            executer: a LivingEntity that was the perpetrator of the attack
            elemental_inflict: if the damage inflicted elemental damage
            critical: if the hit was critical
            miss: if the attack missed
        """
        super().__init__("attack")
        self.damage = damage
        self.is_elemental_damage = elemental_damage
        self.elemental_type = elemental_type
        self.elemental_inflict = elemental_inflict
        self.target = target
        self.executer = executer
        self.critical = critical
        self.miss = miss

    def __repr__(self):
        return f"AttackPacket: {self.damage} damage from {self.executer} to {self.target}"

class DefensePacket(InformationPacket):
    """ A Packet that holds information about defending """

    def __init__(self, user, defense: int, defense_increase: int):
        """ Constructor for a defense packet 
        
            user: the LivingEntity who defended
            defense: the defense they have after defending
            defense_increase: the amount of defense gained from defending
        """
        super().__init__("defense")
        self.user = user
        self.defense = defense
        self.defense_increase = defense_increase

    def __repr__(self):
        return f"DefensePacket: {self.user} increased defense by {self.defense_increase}"
    
class HealthPacket(InformationPacket):
    """ A Packet that has information about healing actions """
    def __init__(self, user, heal_amount: int, healed_to_max: bool):
        """ Constructor for a healing packet

            user: the LivingEntity who healed
            heal_amount: the amount of health gained
            healed_to_max: if the healing brought you to max health
        """
        super().__init__("heal")
        self.user = user
        self.heal_amount = heal_amount
        self.healed_fully = healed_to_max

class FleePacket(InformationPacket):
    """ A Packet that gives information about fleeing """

    def __init__(self, coward):
        super().__init__("flee")
        self.coward = coward
