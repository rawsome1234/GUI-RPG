from info_parser import *
from info_classes import *
from entities import *
import random
import pygame
from pygame_class_handlers import *
from packets import *

current_area: Area = None
current_enemy: EnemyInstance = None
player: PlayerHandler = PlayerHandler()

def get_next_area() -> Area:
    """ gets the next area based on the current area tier """
    global current_area
    global shop_item_list
    shop_item_list.clear()
    tier = -1
    if type(current_area) == Area:
        tier = current_area.tier
    areas_to_select = get_areas_of_tier(tier+1)
    # print(areas_to_select)
    current_area = random.choice(areas_to_select)
    return current_area

def get_next_enemy() -> EnemyInstance:
    """ gets a random enemy from the current area """
    global current_enemy
    global encounters_left
    encounters_left -= 1
    enemy_info = random.choice(current_area.enemies)
    if current_area.tier == 6:
        enemy_info = current_area.enemies[0]
        if random.randint(0,99) == 69:
            enemy_info = current_area.enemies[2]
    current_enemy = EnemyInstance(enemy_info)
    return current_enemy

def give_start_weapon() -> Weapon:
    """ gives the player a random weapon """
    weapon = random.choice(random_weapons).copy()
    player.weapon = weapon
    player.weapon_options.append(weapon)
    # for i in range(25):
    #     weapon = random.choice(random_weapons).copy()
    #     player.weapon_options.append(weapon)
    return weapon

def get_weapon(weapon_list):
    """ gets a random weapon from weapon_list based on weight 

        weapon_list: the list of Weapon objects to pull from
    """
    # calculate the weighting
    weight = 0
    weight = sum([rarity_to_weight(weapon.rarity) for weapon in weapon_list if type(weapon) == Weapon])

    # get the winning number
    lottery = random.randint(0, weight)

    # get the weapon
    running_weight = 0
    for weapon in weapon_list:
        w = rarity_to_weight(weapon.rarity)
        if lottery <= running_weight + w:
            return weapon.copy()
        running_weight += w
    
def rarity_to_weight(rarity):
    """ takes a rarity and returns the weight associated 

        rarity: a string that represents a rarity
    """
    weights = [5, 4, 3, 1]
    match rarity:
        case "common":
            return weights[0]
        case "uncommon":
            return weights[1]
        case "rare":
            return weights[2]
        case "legendary":
            return weights[3]
    return 0
        
def generate_shop_list():
    """ clears and creates the list of items to fill the shop """
    global shop_item_list
    global potions_awarded
    shop_item_list = []
    items = []
    normal_items = random.randint(6, 10)
    special_items_count = 10 - normal_items

    for i in range(normal_items):
        items.append(get_weapon(shop_items))

    for i in range(special_items_count):
        items.append(random.choice(special_items))

    location = [40, 10]
    increment = 45
    for listing in range(len(items)):
        shop_item_list.append(ShopButtonSet(items[listing], location.copy(), listing, items[0], current_area.get_inflation()))
        location[1] += increment
    if potions_awarded:
        add_potion_to_shop()

def add_potion_to_shop():
    """ adds potions to the current shop. Hardcoded to be in a certain position """
    global shop_item_list
    shop_item_list.append(ShopButtonSet(SpecialItem("Potion", "heal", 40, 20), (40, 460), 10, get_weapon(shop_items), current_area.get_inflation()))

def assemble_garage(page_num=1):
    """ creates the list of items to display on a page in the garage 
    
        page_num: the page number to show. Defaults to page 1
    """
    global garage_list
    global garage_page
    garage_list = []
    garage_page = page_num

    location = [40, 10]
    increment = 45
    for listing in range(min((page_num-1)*10, len(player.weapon_options)), min(page_num*10, len(player.weapon_options))):
        garage_list.append(GarageButtonSet(player.weapon_options[listing], location.copy(), listing, player.weapon_options[0], player.weapon_options[listing] == player.weapon))
        location[1] += increment

    return (page_num > 1, len(player.weapon_options) > page_num*10)
        
def attack():
    """ called when the player chooses to attack """
    return player.attack_other(current_enemy)

def defend():
    """ called when the player chooses to defend """
    # print("defending")
    return player.increase_defense()

def enemy_turn():
    """ called for the enemy to take their turn """
    return current_enemy.take_turn(player)

def use_potion():
    """ called when the player chooses to heal using a potion """
    player.potions -= 1
    return player.heal(40)

def flee():
    """ called when the player chooses to flee like a coward """
    return FleePacket(player)

def make_text(packet):
    """ makes the text that the text at the top left will print out based on a packet """
    packet_type = packet.type
    # if it's an attack packet
    if packet_type == "attack":
        attack_packet: AttackPacket = packet

        # if the damage is not elemental
        if not attack_packet.is_elemental_damage:
            name = attack_packet.executer.format_name()
            if attack_packet.miss:
                return f"{name} missed the attack!"
            
            string = f"{name} "

            if attack_packet.critical:
                string += f"got a crit! and "

            string += f"did {attack_packet.damage} damage to {attack_packet.target.get_name()}"

            # if the attack inflicted elemental damage
            if attack_packet.elemental_inflict:
                string += f", inflicting {attack_packet.elemental_type} damage"

        # the damage is elemental
        else:
            string = f"{attack_packet.target.format_name()} took {attack_packet.damage} {attack_packet.elemental_type} damage!"

        return string
    
    # if it's a defense packet
    elif packet_type == "defense":
        defense_packet: DefensePacket = packet
        name = defense_packet.user.format_name()
        string = f"{name} increased their defense by {defense_packet.defense_increase}."
        return string
    
    # if it's a flee packet
    elif packet_type == "flee":
        flee_packet: FleePacket = packet
        coward = flee_packet.coward.format_name()
        string = f"{coward} are going to flee!"
        return string

    elif packet_type == "heal":
        heal_packet: HealthPacket = packet
        user = heal_packet.user.format_name()
        string = f"{user} healed themselves by {heal_packet.heal_amount}"
        
        if heal_packet.healed_fully:
            string += ", healing to full"
        
        string += "!"
        return string

    return ""

def next_area():
    """ gets an area in the next tier and sets the first enemy """
    get_next_area()
    global encounters_left
    encounters_left = current_area.encounters
    get_next_enemy()

def main():
    """ the main function that makes the game run """
    global game_state
    global garage_page
    global garage_list
    parse_info()
    give_start_weapon()

    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption('Turn Based RPG But With GUI')    

    run = True
    frame = 0
    # current_text = ""
    # text_location = (400, 300)
    black = (0,0,0)

    game_state = "start_area"
    global state_drawn
    state_drawn = False

    buttons = []
    labels = []
    highlight_zones = []
    global shop_item_list
    shop_item_list = []

    generic_purchase_item = SpecialItem("Purchased", "","",0)

    def check_enemy_death():
        # if the enemy has perished
        global game_state
        global state_drawn
        global current_enemy
        if not current_enemy.is_alive():
            if current_area.tier == 6:
                if "shadow" in current_enemy.get_name().lower():
                    current_enemy = EnemyInstance(current_area.enemies[1])
                    refresh_screen()
                    Label((400, 110), "The shadowy figure staggers backward. It seems as though it may collapse.", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    Label((400, 140), "He reaches into its cloak, grabs a potion and drinks it.", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    Label((400, 170), "The figure stands up straight, weapon drawn, ready to continue the fight.", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    state_drawn = False
                    
                elif "sans" in current_enemy.get_name().lower():
                    refresh_screen()
                    Label((400, 110), "!!", 20).draw(screen)
                    pygame.display.update()
                    pygame.time.wait(1500)
                    
                    Label((400, 140), "Sans' voice whispers through the void..", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    
                    Label((400, 170), ". ... ... so... guess that's it, huh?", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)

                    Label((400, 200), "Well. Good job. Good luck out there..", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    game_state = "finished"
                    state_drawn = False
                else:
                    refresh_screen()
                    Label((400, 110), "The figure staggers backward, and collapses onto his knee.", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    Label((400, 140), "Its voice crackles out. \n\"I see. You truly are incredible..\"", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(1500)
                    Label((400, 200), "\"Good luck out there...\"", 20).draw(screen, "center")
                    pygame.display.update()
                    pygame.time.wait(2000)
                    game_state = "finished"
                    state_drawn = False


                return True
            else:

                Label(location, f"You killed the {current_enemy.name} and gained {current_enemy.enemy_info.coins_dropped}!", 20).draw(screen)
                progress_state()
                player.coins += current_enemy.enemy_info.coins_dropped
                pygame.display.update()
                pygame.time.wait(750)
                return True
        return False

    def refresh_screen():
        screen.fill(black)

    def show_all():
        for l in labels:
            l.draw(screen, "center")

        for b in buttons:
            b.draw_on_screen(screen)

    def progress_state():
        global game_state
        global state_drawn
        match game_state:
            case "start_area":
                game_state = "battle"
            case "exit_rest":
                game_state = "battle"
            case "battle":
                game_state = "rest"
            case "rest":
                if current_area.encounters >= player.encounters:
                    game_state = "start_area"
                    player.encounters = 0
                else:
                    game_state = "battle"
        state_drawn = False

    def update_stat_text():
        ret = ""
        ret += f"{current_enemy.health}/{current_enemy.enemy_info.health} HP"
        ret += f"\n{current_enemy.enemy_info.damage} damage"
        ret += f"\n{current_enemy.defense} defense"
        if current_enemy.enemy_info.elemental_type.lower() == "none":
            ret += f"\nNo elemental damage"
        else:
            ret += f"\n{current_enemy.enemy_info.elemental_damage} {current_enemy.enemy_info.elemental_type} elemental damage"
        return ret
    
    def attack_update():
        return f"You will deal {max(player.weapon.damage - current_enemy.defense, 0)} damage"

    def defense_update():
        return f"Increase defense by {player.defenseLower}-{player.defenseUpper}"

    def coins_update():
        return f"Coins: {player.coins}"

    def update_player_stats():
        ret = ""
        ret += f"Health: {player.health}/{player.base_health}    Defense: {player.defense}"
        if player.elemental_damage_turns > 0:
            ret += f"     Turns of {player.elemental_damage_amount} {player.elemental_damage_type} Damage: {player.elemental_damage_turns}"
        return ret

    def rest_player_stats():
        def get_space():
            return "      "
        def to_percent(chance):
            return f"{round(chance, 3) * 100}%"

        ret = ""
        # health
        ret += f"              {player.health}/{player.base_health} HP" + get_space()

        # miss chance
        ret += f"{to_percent(player.miss_chance)} miss chance\n"

        # defense
        ret += f"           {player.base_defense} base defense" + get_space()

        # defense increases
        ret += f"{player.defenseLower}-{player.defenseUpper} defense increases\n"

        # crit chance
        ret += f"      {to_percent(player.critical_chance)} critical chance" + get_space()

        # crit multiplier
        ret += f"{to_percent(player.critical_multiplier)} critical multiplier"

        return ret

    def potions_text_update():
        return f"Potions: {player.potions}"

    global encounters_left
    encounters_left = 0
    area_weapon_awarded = False
    fled = False
    global potions_awarded
    potions_awarded = False

    while run:

        if not state_drawn:
            buttons.clear()
            labels.clear()
            highlight_zones.clear()
            refresh_screen()

        # Make the intro to an area
        if not state_drawn:
            match game_state:
                case "start_area":
                    next_area()
                    area_weapon_awarded = False
                    shop_item_list.clear()
                    if current_area.tier == 6:
                        labels.append(Label((400,110), f"You find yourself in the void.", 20))
                        labels.append(Label((400,140), f"There is nothing around you except empty space.", 20))
                        labels.append(Label((400,170), f"Through the darkness, you can see a figure approach...", 20))

                        show_all()

                        pygame.display.update()
                        pygame.time.wait(1500)

                        string = "A shadowy figure approachs you through the void."
                        if current_enemy.get_name().lower()[0] == "s":
                            string = "Sans approaches you through the void!"

                        labels.append(Label((400,200), string, 20))
                    else:
                        labels.append(Label((400, 110), f"You find yourself in a {current_area.name}.", 20))
                        labels.append(Label((400, 140), f"You have a {player.weapon.name} equipped.", 20))
                        labels.append(Label((400, 170), f"Up ahead you see a {current_enemy.enemy_info.name}", 20))
                    # labels.append(Label((10, 30), ))
                    # labels.append(Label((10, 50), ))
                    buttons.append(Button((700,500), ">", 50, 50, "center", action="continue"))
                    
                    show_all()

                    state_drawn = True

                # The base battle scene
                case "battle":
                    highlight_zones.clear()

                    # if the enemy is taking elemental damage change the text color
                    enemy_name_color = (255, 255, 255)
                    if current_enemy.is_taking_elemental_damage():
                        enemy_name_color = (255, 99, 79)

                    # Enemy name
                    labels.append(Label((400, 140), f"{current_enemy.enemy_info.name}", 32, color=enemy_name_color))
                    stats_location = (400, 500)
                    
                    # potion button if they're available
                    if player.potions > 0:
                        buttons.append(Button((400, 470), "Potion", 120, 50, "center", action="potion"))
                        highlight_zones.append(HighlightZone((400, 470), f"Potions left: {player.potions}", 120, 50, 150, 40, "center", textupdate=potions_text_update))
                        stats_location = (400, 540)

                    labels.append(Label(stats_location, "player info", 20, update_player_stats))

                    buttons.append(Button((250, 400), "Attack", 120, 50, "center", action="attack"))
                    buttons.append(Button((400, 400), "Defense", 120, 50, "center", action="defend"))
                    buttons.append(Button((550, 400), "Flee", 100, 50, "center", action="flee"))

                    highlight_zones.append(HighlightZone((400,140), "ENEMY", 120, 50, 330, 120, "center", update_stat_text))
                    highlight_zones.append(HighlightZone((250,400), "ATTACK DAMAGE", 120, 50, 270, 30, "center", textupdate=attack_update))
                    highlight_zones.append(HighlightZone((400,400), "DEFENSE", 120, 50, 270, 30, "center", textupdate=defense_update))
                    highlight_zones.append(HighlightZone((550,400), "Escape without healing,\nbut the enemy still\ntakes their turn", 120, 50, 260, 100, "center"))

                    show_all()
                    state_drawn = True

                # The main rest screen
                case "rest":
                    if not fled:
                        player.rest()
                    if encounters_left == 0 and not area_weapon_awarded:
                        area_weapon_awarded = True
                        area_weapon = get_weapon(current_area.weapons)
                        player.weapon_options.append(area_weapon)
                        labels.append(Label((400,200), f"The {current_enemy.name} dropped a {area_weapon.name}! Equip it in the garage!", 24))
                    
                    if encounters_left == 0 and current_area.tier == 3 and not potions_awarded:
                        labels.append(Label((400,240), f"Potions are now available to purchase in the shop!", 24))
                        add_potion_to_shop()
                        potions_awarded = True


                    labels.append(Label((400, 150), "~~~[ Rest ]~~~", 32))
                    labels.append(Label((400, 500), "PLAYER STATS", 20, rest_player_stats))

                    buttons.append(Button((300, 300), "Shop", 120, 50, "center", action="shop"))
                    buttons.append(Button((500, 300), "Garage", 120, 50, "center", action="garage"))
                    buttons.append(Button((400, 400), "Exit", 120, 50, "center", action="exit_rest"))

                    highlight_zones.append(HighlightZone((300,300), "Buy items and weapons", 120, 50, 270, 30, "center"))
                    highlight_zones.append(HighlightZone((500,300), "Change weapon \nand equip items", 120, 50, 180, 60, "center"))
                    highlight_zones.append(HighlightZone((400,400), f"Encounters left: {encounters_left}", 120, 50, 200, 30, "center"))

                    show_all()
                    state_drawn = True

                # The shop menu
                case "shop":
                    
                    if shop_item_list == []:
                        generate_shop_list()
                        
                    labels.append(Label((75, 550), "Coins: x", 24, coins_update))
                    
                    labels[0].draw(screen, "center")
                    
                    for item in shop_item_list:
                        item.draw(screen)
                        buttons.append(item.purchase_button)

                    buttons.append(Button((700, 550), "Exit Shop", 120, 40, "center", action="rest"))
                    buttons[-1].draw_on_screen(screen)
                    
                    state_drawn = True

                # the garage menu
                case "garage":

                    multiple_pages = assemble_garage(garage_page)
                    if multiple_pages[0]:
                        buttons.append(Button((100, 500), "< Page", 120, 40, "center", action="garage_page_left"))
                    if multiple_pages[1]:
                        buttons.append(Button((700, 500), "Page >", 120, 40, "center", action="garage_page_right"))

                    for item in garage_list:
                        item.draw(screen)
                        buttons.append(item.select_button)

                    buttons.append(Button((700, 550), "Exit Garage", 140, 40, "center", action="rest"))
                    
                    show_all()
                    
                    state_drawn = True
                    
                case "exit_rest":
                    fled = False
                    if encounters_left > 0:
                        get_next_enemy()
                        Label((400, 170), f"Up ahead you see a {current_enemy.enemy_info.name}", 20).draw(screen, "center")
                        # labels.append(Label((10, 30), ))
                        # labels.append(Label((10, 50), ))
                        buttons.append(Button((700,500), ">", 50, 50, "center", action="continue"))
                        buttons[-1].draw_on_screen(screen)

                        state_drawn = True
                    else:
                        game_state = "start_area"
                        state_drawn = False

                case "finished":
                    labels.append(Label((400, 110), "Thank you for playing!", 20))
                    labels.append(Label((400, 140), "To quit, press the button below.", 20))

                    buttons.append(Button((400, 400), "Quit", 120, 40, "center", action="quit"))

                    show_all()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


            for b in buttons:
                    if b.is_hovered(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                        if b.action == "continue":
                            progress_state()
                        if b.action == "quit":
                            run = False
                        
                        if b.action == "shop":
                            game_state = "shop"
                            state_drawn = False

                        if b.action == "garage":
                            garage_page = 1
                            game_state = "garage"
                            state_drawn = False
                        
                        if b.action == "rest":
                            game_state = "rest"
                            state_drawn = False

                        if len(b.action) > 4 and b.action[:4] == "shop":
                            index = int(b.action[4:])
                            purchase = shop_item_list[index].weapon
                            if player.can_purchase_weapon(purchase, current_area.get_inflation()):
                                if index == 10:
                                    player.potions += 1
                                    player.coins -= int(purchase.price * current_area.get_inflation())
                                else:
                                    shop_item_list[index].weapon = generic_purchase_item
                                    shop_item_list[index].create_button()
                                    shop_item_list[index].create_info_label()
                                    player.purchase_item(purchase, current_area.get_inflation())
                                state_drawn = False
                            else:
                                Label((150, 525), "You don't have enough coins!", 20).draw(screen,"center")
                                pygame.display.update()
                                pygame.time.wait(400)
                        
                        # page left button
                        if b.action == "garage_page_left":
                            garage_page -= 1
                            state_drawn = False
                        
                        # page right button
                        elif b.action == "garage_page_right":
                            garage_page += 1
                            state_drawn = False

                        # selecting in garage
                        elif len(b.action) > 6 and b.action[:6] == "garage":
                            index = int(b.action[6:])
                            selection = garage_list[index].weapon
                            if type(selection) == SpecialItem:
                                player.weapon_options.remove(selection)
                                selection.apply_to_player(player)
                            else:
                                player.weapon = selection
                                
                            state_drawn = False
                        

                        if b.action == "exit_rest":
                            game_state = "exit_rest"
                            state_drawn = False
                            break


                        player_action = None
                        if b.action == "attack":
                            player_action = attack
                        if b.action == "defend":
                            player_action = defend
                        if b.action == "flee":
                            player_action = flee
                        if b.action == "potion":
                            player_action = use_potion

                        # this will only occur if the player has pressed a button
                        if player_action != None:
                            # refreshes the screen without the buttons
                            buttons.clear()
                            refresh_screen()
                            show_all()

                            # gets the player packet
                            packet = player_action()

                            location = [10, 10]
                            increment = 20

                            # shows the action
                            p_text = make_text(packet)
                            player_action_label = Label(location, p_text, 20)
                            player_action_label.draw(screen)
                            
                            # updates the screen to show the label
                            pygame.display.update()

                            pygame.time.wait(500)

                            location[1] += increment

                            if check_enemy_death():
                                break

                            # gets the enemy packet and displays it
                            enemy_packet = enemy_turn()
                            e_text = make_text(enemy_packet)
                            enemy_action_label = Label(location, e_text, 20)
                            enemy_action_label.draw(screen)

                            
                            pygame.display.update()

                            pygame.time.wait(500)

                            location[1] += increment

                            # handle elemental damages
                            pe_packet = player.take_elemental_damage()
                            # if the player took elemental damage
                            if pe_packet != False:
                                pe_text = make_text(pe_packet)
                                p_elemental_action_label = Label(location, pe_text, 20)
                                p_elemental_action_label.draw(screen)

                                pygame.display.update()

                                pygame.time.wait(500)

                                # increment location for next line
                                location[1] += increment
                            
                            ee_packet = current_enemy.take_elemental_damage()
                            # if the enemy took elemental damage
                            if ee_packet != False:
                                ee_text = make_text(ee_packet)
                                e_elemental_action_label = Label(location, ee_text, 20)
                                e_elemental_action_label.draw(screen)

                                pygame.display.update()

                                pygame.time.wait(500)

                                # increment location for next line
                                location[1] += increment

                            if check_enemy_death():
                                break

                            # end elementals
                            if pe_packet != False:
                                elemental_type = player.elemental_damage_type
                                res = player.end_elemental()
                                if res:
                                    p_end_element_label = Label(location, f"{player.format_name()} is no longer taking {elemental_type} damage!", 20)
                                    p_end_element_label.draw(screen)

                                    pygame.display.update()

                                    pygame.time.wait(500)

                                    location[1] += increment

                            if ee_packet != False:
                                elemental_type = current_enemy.elemental_damage_type
                                res = current_enemy.end_elemental()
                                if res:
                                    e_end_element_label = Label(location, f"{current_enemy.format_name()} is no longer taking {elemental_type} damage!", 20)
                                    e_end_element_label.draw(screen)

                                    pygame.display.update()

                                    pygame.time.wait(500)

                                    location[1] += increment

                            
                            if not player.is_alive():
                                Label(location, "You have failed in your mission and perished..", 20).draw(screen)
                                pygame.display.update()
                                pygame.time.wait(5000)
                                run = False
                                
                            if packet.type == "flee":
                                game_state = "rest"
                                fled = True
                                state_drawn = False
                            
                            # mark for the buttons to be redrawn
                            state_drawn = False

                            pygame.time.wait(500)


                        # print("Button is hovered")
            
            to_display = []
            for h in highlight_zones:
                if h.is_hovered(pygame.mouse.get_pos()):
                    to_display.append(h)

            
            if len(to_display) > 0:
                refresh_screen()
                show_all()
                for h in to_display:
                    h.showTip(screen)

            elif len(highlight_zones) > 0:
                refresh_screen()
                show_all()

                
        frame += 1
        pygame.display.update()
        # pygame.time.wait()

    pygame.quit()

if __name__ == "__main__":
    main()