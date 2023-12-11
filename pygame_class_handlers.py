import pygame
from info_parser import *
from info_classes import *
from entities import *

class Button():
    """ A button class to detect and activate actions """
    def __init__(self, location, text, width, height, alighment="topleft", name="none", action="none"):
        """ Constructor method for a button

            location: the location to draw the button
            text: the text to draw on the button
            width: the width of the button
            height: the height of the button
            alighment: the alignment of the button. Defaults to topleft. Center is the other acceptable input
            name: the name of the button. Unused
            action: the action string the button stores
        """
        if alighment == "center":
            location = (location[0]-(.5 * width), location[1]-(.5*height))
        center = (location[0]+(.5 * width), location[1]+(.5*height))
        self.label = Label(center, text, 24)
        self.location = location
        self.text = text
        self.width = width
        self.height = height
        self.light = (150, 150, 150)
        self.dark = (100, 100, 100)
        self.action = action
        self.name = name

    def draw_on_screen(self, screen: pygame.Surface):
        offset = 4
        pygame.draw.rect(screen, self.dark, [self.location[0], self.location[1], self.width, self.height])
        pygame.draw.rect(screen, self.light, [self.location[0]+offset, self.location[1]+offset, self.width-(offset*2), self.height-(offset*2)])
        self.label.draw(screen, "center")

    def is_hovered(self, mouse_pos):
        return self.location[0] <= mouse_pos[0] <= self.location[0]+self.width and self.location[1] <= mouse_pos[1] <= self.location[1]+self.height
    
class Label():
    """ A class that draws text on a display """

    def __init__(self, location, text, font_size=16, update_method=None, color=(255, 255, 255)):
        """ The constructor for a text object 
        
            location: the location for the text to be drawn
            text: the text that will be displayeed
            font_size: the size of the text. Defaults to 16
            update_method: a method reference that will update the text. Defaults to None
        """
        self.location = location
        self.text = text
        self.color = color
        self.black = (0, 0, 0)
        self.font_size = font_size
        self.update_method = update_method

    def relocate(self, new_location):
        self.location = new_location
        
    def draw(self, screen, alignment="topleft"):
        if self.update_method != None:
            self.text = self.update_method()

        font = pygame.font.Font('Roboto-Regular.ttf', self.font_size)
        pygame.font.Font()
        lines = self.text.split("\n")
        running_location = self.location
        for line in lines:
            out = font.render(line, True, self.color)  

            textRect = out.get_rect()
            match alignment:
                case "center":
                    textRect.center = running_location
                case "topleft":
                    textRect.topleft = running_location
            
            # screen.fill(black)
            screen.blit(out, textRect)
            running_location = (running_location[0], running_location[1]+30)
    
class HighlightZone():

    def __init__(self, location, text, zone_width, zone_height, text_back_width, text_back_height, alighment="topleft", textupdate=None):
        """ constructor for a highlight zone
        
            location: the location where the zone will be
            text: the text the zone will put on screen
            zone_width: the width of the zone
            zone_height: the height of the zone
            text_back_width: the width of the box behind the tooltip
            text_back_height: the height of the box behind the tooltip
            alighment: the alignment of the button. Defaults to topleft. Center is the other acceptable input
            textupdate: a method reference that will update the text. Defaults to None
        """
        location = (location[0]+3, location[1])
        if alighment == "center":
            location = (location[0]-(.5 * zone_width), location[1]-(.5*zone_height))
        center = (location[0]+(.5 * zone_width), location[1]+(.5*zone_height))
        self.label = Label(center, text, 24, textupdate)
        self.location = location
        self.text = text
        self.zone_width = zone_width
        self.zone_height = zone_height
        self.text_back_width = text_back_width
        self.text_back_height = text_back_height
        self.light = (150, 150, 150)
        self.dark = (100, 100, 100)

    def is_hovered(self, mouse_pos):
        return self.location[0] <= mouse_pos[0] <= self.location[0]+self.zone_width and self.location[1] <= mouse_pos[1] <= self.location[1]+self.zone_height
    
    def showTip(self, screen):
        offset = 3
        mouse_pos = pygame.mouse.get_pos()
        draw_cords = (mouse_pos[0]+16, mouse_pos[1])
        self.label.relocate(draw_cords)
        pygame.draw.rect(screen, self.dark, [draw_cords[0]-4, draw_cords[1], self.text_back_width, self.text_back_height])
        self.label.draw(screen, "topleft")
        
        # screen.blit(self.label, (mouse_pos[0]+16, mouse_pos[1]))

class ShopButtonSet():
    """ A button and labels to describe a weapon """

    def __init__(self, weapon, location, index, example_weapon, inflation):            
        """ A constructor for a shop listing

            weapon: the weapon or item being added
            location: the location where the button will be placed, with information to its right
            index: the shop index of this item
            example_weapon: Because python is dumb and stupid and broken this is needed
        """
        self.location = location
        self.weapon = weapon
        self.example = example_weapon
        self.shop_index = index
        self.create_button()
        self.create_info_label()
        self.inflation = inflation

    def create_button(self):
        location = (self.location[0], self.location[1])
        width = 200
        if "defense" in self.weapon.name.lower():
            width = 250
        self.purchase_button = Button(location, f"{self.weapon.name}", width, 40, "topleft", action="shop"+str(self.shop_index))

    def update_text(self):
        price = self.weapon.price
        ret = f"Price: {int(price * self.inflation)}"
        if type(self.weapon) == type(self.example):
            if price < 100:
                ret += "  "
            if price < 10:
                # print("adding an extra space")
                ret += "   "
            ret += f"           {self.weapon.damage} damage"
            if self.weapon.elemental_type != "none":
                ret += f"           {self.weapon.elemental_damage} {self.weapon.elemental_type}"
        elif self.weapon.name.lower() != "purchased":
            ret += f"            +{self.weapon.modifier_amount} {self.weapon.modifier_type}"
        return ret

    def create_info_label(self):
        location = (self.location[0] + 200 + 75, self.location[1])
        self.label = Label(location, "info text", 24, self.update_text)

    def draw(self, screen):
        self.label.draw(screen)
        self.purchase_button.draw_on_screen(screen)

class GarageButtonSet():
    """ A button and labels to describe a weapon """

    def __init__(self, weapon, location, index, example_weapon, selected):            
        """ A constructor for a garage listing

            weapon: the weapon or item being added
            location: the location where the button will be placed, with information to its right
            index: the garage index of this item
            example_weapon: Because python is dumb and stupid and broken this is needed
            selected: if this weapon is selected
        """
        self.location = location
        self.weapon = weapon
        self.example = example_weapon
        self.garage_index = index
        self.selected = selected
        self.create_button()
        self.create_info_label()

    def create_button(self):
        location = (self.location[0], self.location[1])
        width = 200
        if "defense" in self.weapon.name.lower():
            width = 250
        self.select_button = Button(location, f"{self.weapon.name}", width, 40, "topleft", action="garage"+str(self.garage_index))

    def toggle_selected(self):
        self.selected = not self.selected

    def update_text(self):
        ret = "          "
        if self.selected:        
            ret = "(selected)"
        if type(self.weapon) == type(self.example):
            ret += f"    {self.weapon.damage} damage"
            if self.weapon.elemental_type != "none":
                ret += f"     {self.weapon.elemental_damage} {self.weapon.elemental_type}"
        elif self.weapon.name.lower() != "purchased":
            ret += f"        +{self.weapon.modifier_amount} {self.weapon.modifier_type}"
        return ret

    def create_info_label(self):
        location = (self.location[0] + 200 + 75, self.location[1])
        self.label = Label(location, "info text", 24, self.update_text)

    def draw(self, screen):
        self.label.draw(screen)
        self.select_button.draw_on_screen(screen)