
"""

TODO:  add container limitation
TODO:  Define dominant hand. Current default dominant hand is right hand
TODO:  Define health leveling function after 0.
"""

import random as random
import time as time
import textwrap as textwrap
import threading as threading
import pathlib as pathlib
import pickle as pickle
import math as math

import config as config
import world as world
import quests as quests
import combat as combat
import mixins as mixins
import actions as actions
import npcs as npcs
import interface as interface
import items as items

wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)
commands = {}
global character
global terminal_output
available_stat_points = config.available_stat_points
profession_stats_growth_file = config.PROFESSION_STATS_GROWTH_FILE
race_stats_file = config.RACE_STATS_FILE
all_items = mixins.all_items
all_items_categories = mixins.items
lock = threading.Lock()


def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal


def create_character(character_name=None):
    global character
    character = Player(player_name=character_name)


class Player(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, player_name: str, **kwargs):

        self.player_data = self.get_player_by_name(name=player_name)

        self.name = self.player_data['first_name']
        self.first_name = self.player_data['first_name']
        self.last_name = self.player_data['last_name']
        self.gender = self.player_data['gender']
        self.race = self.player_data['race']
        self.profession = self.player_data['profession']
        self.object_pronoun = None
        self.possessive_pronoun = None
        self.level = self.player_data['level']
        self.experience = self.player_data['experience']

        self.stats_base = self.player_data['stats']
        self.stats = self.player_data['stats']

        self.stats_bonus = self.player_data['stats_bonus']

        self.training_points = self.player_data['training']

        self.physical_points = self.player_data['training']['physical_points']
        self.mental_points = self.player_data['training']['mental_points']

        self.skills_base = self.player_data['skills']
        self.skills = self.player_data['skills']
        self.skills_bonus = self.player_data['skills_bonus']
        
        self.health = self.player_data['health']
        self.health_max = self.player_data['health']

        self.attack_strength_base = 0

        self.defense_strength_evade_base = 0
        self.defense_strength_block_base = 0
        self.defense_strength_parry_base = 0
        
        self.mana = self.player_data['mana']

        self.money = self.player_data['money']

        self.inventory = []

        for category in self.player_data['inventory']:
            for item in self.player_data['inventory'][category]:
                self.inventory.append(items.create_item(item_category=category, item_name=item))

        self.right_hand_inv = None
        if len(self.player_data['right_hand']['item_name']) != 0:
            self.right_hand_inv.append(items.create_item(item_category=player_data['right_hand']['item_category'], item_name=player_data['right_hand']['item_name']))

        self.left_hand_inv = None
        if len(self.player_data['left_hand']['item_name']) != 0:
            self.left_hand_inv.append(items.create_item(item_category=player_data['left_hand']['item_category'], item_name=player_data['left_hand']['item_name']))

        self.dominance = "right_hand"
        self.non_dominance = "left_hand"

        self.location_x, self.location_y = world.starting_position
        self.room = world.tile_exists(x=self.location_x, y=self.location_y, area='Field')
        self.area = 'Field'

        self.target = None
        self.rt_start = 0
        self.rt_end = 0

        self.quests = {}

        for quest in self.player_data['quests']:
            self.quests[quest] = quests.Quest(quest_name=quest, character=self)
            self.quests[quest].start()

    def level_up(self):
        
        self.level += 1
        
        for stat in self.stats:
            self.stats[stat] = self.stats[stat] + 1 / (self.stats[stat] / int(profession_stats_growth_file.loc[self.profession][stat]))
            if self.stats[stat] > 100:
                self.stats[stat] = 100
        
            self.stats_bonus[stat] = ((self.stats[stat] - available_stat_points / 8) / 2 + int(race_stats_file.loc[self.race][stat]))
        
        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = self.health
        
        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))      
        

    def set_character_attributes(self):
        for stat in self.stats:
            self.stats_bonus[stat] = ((self.stats[stat] - available_stat_points / 8) / 2 + int(race_stats_file.loc[self.race][stat]))

        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = self.health
        
        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))

    def set_gender(self, gender):
        if gender == "female":
            self.gender = gender
            self.object_pronoun = "She"
            self.possessive_pronoun = "Her"
        if gender == "male":
            self.gender = gender
            self.object_pronoun = "He"
            self.possessive_pronoun = "His"

    def test(self, **kwargs):
        area_rooms = world.area_rooms(self.area)
        print(random.choice(list(area_rooms)))

    def add_money(self, amount):
        with lock:
            self.money += amount

    def subtract_money(self, amount):
        with lock:
            self.money -= amount

    def is_dead(self):
        if self.health > 0:
            return False
        else:
            terminal_output.print_text("You're dead! You will need to restart from your last saved point.")
            return True

    def check_round_time(self):
        with lock:
            round_time = False
            if time.time() < self.rt_end:
                terminal_output.print_text("Remaining round time: " + str(round(self.rt_end - time.time())) + " sec...")
                round_time = True
        return round_time

    def set_round_time(self, seconds):
        with lock:
            self.rt_start = time.time()
            self.rt_end = self.rt_start + seconds
        return
    
    def get_stat(self, stat):
        with lock:
            return self.stats[stat]
        
    def get_stat_bonus(self, stat):
        with lock:
            return self.stats_bonus[stat]
    
    def get_skill(self, skill):
        with lock:
            return self.skills[skill]

    def get_skill_bonus(self, skill):
        with lock:
            return self.skills_bonus[skill]

    def check_inventory_for_item(self, item):
        with lock:
            for inv_item in self.inventory:
                if inv_item == item:
                    return True
                if inv_item.container == True:
                    for sub_inv_item in inv_item.items:
                        if sub_inv_item == item:
                            return True
            if len(self.right_hand_inv) == 1:
                if item == self.get_right_hand_inv():
                    return True
            if len(self.left_hand_inv) == 1:
                if item == self.get_left_hand_inv():
                    return True
            return False

    def all_inventory_handles(self):
        with lock:
            all_inventory_handles = []
            for item in self.inventory:
                all_inventory_handles.append(item.handle)
                if item.container == True:
                    for sub_item in item.items:
                        all_inventory_handles.append(sub_item.handle)
            return all_inventory_handles

    def check_quest(self, quest):
        with lock:
            for quest_self in self.quests:
                if self.quests[quest_self].name == quest.name:
                    return True
            return False

    def add_quest(self, quest_name, quest):
        with lock:
            self.quests[quest_name] = quest

    def __getstate__(self):
        """Copy the object's state from self.__dict__ which contains all our instance attributes. Always use the
        dict.copy() method to avoid modifying the original state."""
        state = self.__dict__.copy()
        del state['room']
        quests_data = {}
        for quest in self.quests:
            quests_data[quest] = self.quests[quest].save()
        state['quests'] = quests_data
        return state

    def __setstate__(self, state):
        """Set the object's state in self.__dict__ which contains all our instance attributes."""
        for quest in state['quests']:
            self.quests[quest] = quests.Quest(quest_name=quest, character=self)
            self.quests[quest].load(state=state['quests'][quest])
            self.quests[quest].start()
        del state['quests']
        self.__dict__.update(state)

    def load(self, state):
        self.__setstate__(state)
        
    def get_right_hand_inv(self):
        with lock:
            if self.right_hand_inv:
                return self.right_hand_inv
            else: return None
    
    def get_left_hand_inv(self):
        with lock:
            if self.left_hand_inv:
                return self.seft_hand_inv
            else: return None
        
    def get_dominant_hand_inv(self):
        if self.dominance == 'right_hand':
            return self.get_right_hand_inv()
        if self.dominance == 'left_hand':
            return self.get_left_hand_inv()
        
    def get_non_dominant_hand_inv(self):
        if self.dominance == 'right_hand':
            return self.get_left_hand_inv()
        if self.dominance == 'left_hand':
            return self.get_right_hand_inv()
    
    def set_right_hand_inv(self, item):
        with lock:
            self.right_hand_inv = item
    
    def set_left_hand_inv(self, item):
        with lock:
            self.left_hand_inv = item
            
    def set_dominant_hand_inv(self, item):
        if self.dominance == 'right_hand':
            self.set_right_hand_inv(item)
        if self.dominance == 'left_hand':
            self.set_left_hand_inv(item)
            
    def set_non_dominant_hand_inv(self, item):
        if self.dominance == 'right_hand':
            self.set_left_hand_inv(item)
        if self.dominance == 'left_hand':
            self.set_right_hand_inv(item)
            
    def get_attack_strength_base(self):
        with lock:
            return self.attack_strength_base
        
    def get_defense_strength_evade_base(self):
        with lock:
            return self.defense_strength_evade_base
        
    def get_defense_strength_block_base(self):
        with lock:
            return self.defense_strength_block_base
        
    def get_defense_strength_parry_base(self):
        with lock:
            return self.defense_strength_parry_base
        

############### VERBS ####################

    def ask(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        elif not kwargs['direct_object']:
            terminal_output.print_text("Who are you trying to ask?")
            return
        elif not kwargs['indirect_object']:
            terminal_output.print_text("What are you trying to ask about?")
            return
        else:
            for npc in self.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    npc.ask_about(object=kwargs['indirect_object'])
                    return
            else:
                terminal_output.print_text("That doesn't seem to do any good.")
                
    def view_attributes(self, **kwargs):
                terminal_output.print_text('''
Attribute:  {}
            '''.format(self.attack_strength_base))

    def attack(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if kwargs['direct_object']:
            self.target = kwargs['direct_object']
        if not self.target:
            terminal_output.print_text("Who are you going to attack? You do not have a target.")
            return
        else:
            for npc in self.room.npcs:
                if set(npc.handle) & set(self.target):
                    terminal_output.print_text("{} will probably not appreciate that.".format(npc.name))
                    return
            enemy_found = False
            for enemy in self.room.enemies:
                if set(enemy.handle) & set(self.target):
                    enemy_found = True
                    combat.melee_attack(self, enemy)
                    self.set_round_time(3)
                    return
            if not enemy_found:
                terminal_output.print_text("{} is not around here.".format(kwargs['direct_object']))
                return

    def drop_item(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        elif not kwargs['direct_object']:
            terminal_output.print_text("I'm sorry, I could not understand what you wanted.")
            return
        elif self.get_dominant_hand_inv() is None:
            terminal_output.print_text("You do not have that item in your hand")
            return
        elif not set(self.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            terminal_output.print_text("You do not have that item in your right hand.")
            return
        else:
            self.room.items.append(self.get_dominant_hand_inv())
            terminal_output.print_text("You drop " + self.get_dominant_hand_inv().name)
            self.get_dominant_hand_inv()
            return

    def flee(self, **kwargs):
        """Moves the player randomly to an adjacent tile"""
        if self.check_round_time():
            return
        if self.is_dead():
            return
        available_moves = self.room.adjacent_moves()
        r = random.randint(0, len(available_moves) - 1)
        actions.do_action(action_input=available_moves[r], character=self)
        return

    def get(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if not kwargs['direct_object']:
            terminal_output.print_text("I'm sorry, I could not understand what you wanted.")
            return
        for room_object in self.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                terminal_output.print_text("Perhaps picking up {} is not a good idea.".format(room_object.name))
                return
        if self.get_dominant_hand_inv() is None:
            item_found = False
            for room_item in self.room.items:
                if set(room_item.handle) & set(kwargs['direct_object']):
                    self.set_dominant_hand_inv(room_item)
                    self.room.items.remove(room_item)
                    terminal_output.print_text("You pick up {}.".format(room_item.name))
                    return
            if not item_found:
                for inv_item in self.inventory:
                    if inv_item.container:
                        for sub_item in inv_item.items:
                            if set(sub_item.handle) & set(kwargs['direct_object']):
                                self.set_dominant_hand_inv(sub_item)
                                inv_item.items.remove(sub_item)
                                terminal_output.print_text("You take {} from {}.".format(sub_item.name, inv_item.name))
                                return
            if not item_found:
                terminal_output.print_text("A " + kwargs['direct_object'][0] + " is nowhere to be found")
        else:
            terminal_output.print_text('You already have something in your right hand')

    def give(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        elif not kwargs['direct_object']:
            terminal_output.print_text("What are you trying to give?")
            return
        elif self.get_dominant_hand_inv() is None:
            terminal_output.print_text("You don't seem to be holding that item in your hand.")
            return
        elif not set(self.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            terminal_output.print_text("You don't seem to be holding that item in your hand.")
            return
        elif not kwargs['indirect_object']:
            terminal_output.print_text("To whom do you want to give?")
            return
        else:
            for npc in self.room.npcs:
                if {npc.first_name.lower()} & set(kwargs['indirect_object']):
                    if npc.give_item(self.get_dominant_hand_inv()):
                        self.get_dominant_hand_inv()
                        return
                    else:
                        return
            terminal_output.print_text("That didn't seem to work.")
            return

    def go(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if not kwargs['direct_object']:
            terminal_output.print_text("Go where?")
            return
        else:
            object_found = False
            for room_object in self.room.objects:
                if set(room_object.handle) & set(kwargs['direct_object']):
                    new_location = room_object.go_object(character=self)
                    self.room = world.tile_exists(x=new_location['x'], y=new_location['y'], area=new_location['area'].replace(" ",""))
                    self.location_x = new_location['x']
                    self.location_y = new_location['y']
                    self.area = new_location['area']
                    self.room.fill_room(character=self)
                    self.room.intro_text()
                    self.room.run(character=self)
                    object_found = True
            if object_found == False:
                for room_item in self.room.items:
                    if set(room_item.handle) & set(kwargs['direct_object']):
                        terminal_output.print_text("You move toward {}.".format(room_item.name))
                        object_found = True
            if object_found == False:
                for room_npc in self.room.npcs:
                    if set(room_npc.handle) & set(kwargs['direct_object']):
                        terminal_output.print_text("You move toward {}.".format(room_npc.name))
                        
    def view_health(self, **kwargs):
        terminal_output.print_text('''
Health:  {} of {} hit points
            '''.format(self.health,
                       self.health_max))

    def view_inventory(self, **kwargs):
        if self.get_dominant_hand_inv():
            right_hand = "You have {} in your {} hand.".format(self.get_dominant_hand_inv().name, self.dominance)
        else:
            right_hand = "Your right hand is empty."
        if self.get_non_dominant_hand_inv():
            left_hand = "You have {} in your {} hand.".format(self.get_non_dominant_hand_inv().name, self.non_dominance)
        else:
            left_hand = "Your left hand is empty."
        inventory_clothing = [x.name for x in self.inventory if x.category == 'clothing']
        if len(inventory_clothing) > 1:
            inventory_clothing = "You are wearing {} and {}.".format(', '.join(inventory_clothing[:-1]), inventory_clothing[-1])
        elif len(inventory_clothing) == 1:
            inventory_clothing = "You are wearing {}.".format(inventory_clothing[0])
        else:
            inventory_clothing = "You are wearing nothing."
        inventory_armor = [x.name for x in self.inventory if x.category == 'armor']
        if len(inventory_armor) > 1:
            inventory_armor ="You are also wearing {} and {}.".format(self.object_pronoun, ', '.join(inventory_armor[:-1]), inventory_armor[-1])
        elif len(inventory_armor) == 1:
            inventory_armor = "You are also wearing {}.".format(self.object_pronoun, inventory_armor[0])
        else:
            inventory_armor = "You are also wearing no armor.".format(self.object_pronoun)
        wealth = "You have {} gulden.".format(self.money)
        terminal_output.print_text('''\
{}
{}
{}
{}
{}
                                    \
                                    '''.format(right_hand,
                                               left_hand,
                                               wrapper.fill(inventory_clothing),
                                               wrapper.fill(inventory_armor),
                                               wrapper.fill(wealth)))

    def look(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if kwargs['preposition'] == None:
            self.room.intro_text()
            return
        if kwargs['preposition'][0] == 'in':
            item_found = False
            if kwargs['indirect_object'] is None:
                terminal_output.print_text("I am not sure what you are referring to.")
                return
            for item in self.room.items + self.room.objects + self.room.npcs + self.inventory + [self.get_right_hand_inv()] + [self.get_left_hand_inv()]:
                if isinstance(item, npcs.NPC):
                    terminal_output.print_text("It wouldn't be advisable to look in " + item.name)
                    return
                if set(item.handle) & set(kwargs['indirect_object']):
                    terminal_output.print_text(item.contents())
                    return
            if item_found is False:
                terminal_output.print_text("A {} is nowhere to be found.".format(kwargs['indirect_object'][0]))
                return
        if kwargs['preposition'][0] == 'at':
            item_found = False
            if kwargs['indirect_object'] is None:
                terminal_output.print_text("I am not sure what you are referring to.")
                return
            for item in self.room.items + self.room.objects + self.room.npcs + self.inventory + [self.get_right_hand_inv()] + [self.get_left_hand_inv()]:
                if set(item.handle) & set(kwargs['indirect_object']):
                    item.view_description()
                    return
            for item in self.inventory:
                if set(item.handle) & set(kwargs['indirect_object']):
                    item.view_description()
                    return
            for object in self.room.objects:
                if set(object.handle) & set(kwargs['indirect_object']):
                    object.view_description()
                    return
            for npc in self.room.npcs:
                if set(npc.handle) & set(kwargs['indirect_object']):
                    npc.view_description()
                    return
            if item_found is False:
                terminal_output.print_text("At what did you want to look?")
                return
        else:
            terminal_output.print_text("I'm sorry, I didn't understand you.")
            return

    def move(self, dx, dy):
        self.location_x += dx
        self.location_y += dy
        self.room = world.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.fill_room(character=self)
        self.room.intro_text()
        return

    def move_north(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        self.move(dx=0, dy=-1)
        return

    def move_south(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        self.move(dx=0, dy=1)
        return

    def move_east(self,**kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        self.move(dx=1, dy=0)
        return

    def move_west(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        self.move(dx=-1, dy=0)
        return

    def put(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if not kwargs['direct_object']:
            terminal_output.print_text("What is it you're trying to put down?")
            return
        elif self.get_dominant_hand_inv() is None:
            terminal_output.print_text("You do not have that item in your hand.")
            return
        elif not set(self.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            terminal_output.print_text("You do not have that item in your right hand.")
            return
        elif kwargs['preposition'][0] == "in":
            for inv_item in self.inventory:
                if set(inv_item.handle) & set(kwargs['indirect_object']):
                    if inv_item.container == False:
                        terminal_output.print_text("{} won't fit in there.".format(self.get_dominant_hand_inv().name))
                        return
                    if len(inv_item.items) == inv_item.capacity:
                        terminal_output.print_text("{} can't hold any more items".format(inv_item.name))
                        return
                    inv_item.items.append(self.get_dominant_hand_inv())
                    terminal_output.print_text("You put {} {} {}".format(self.get_dominant_hand_inv().name, kwargs['preposition'][0], inv_item.name))
                    self.set_dominant_hand_inv(item=None)
                    return
            for room_item in self.room.items:
                if set(room_item.handle) & set(kwargs['indirect_object']):
                    if room_item.container == False:
                        terminal_output.print_text("{} won't fit {} there.".format(self.right_hand_inv[0].name, kwargs['preposition'][0]))
                        return
                    room_item.items.append(self.get_dominant_hand_inv())
                    self.set_dominant_hand_inv(None)
                    terminal_output.print_text("You put {} {} {}".format(self.get_dominant_hand_inv().name, kwargs['preposition'][0], room_item.name))
                    self.set_dominant_hand_inv(None)
                    return
        elif kwargs['preposition'][0] == "on":
            terminal_output.print_text("You cannot stack items yet.")
            return
        else:
            terminal_output.print_text("That item is not around here, unfortunately.")
            return

    def save(self,):
        save_data = self.__getstate__()
        character_name = "{}_{}.p".format(self.first_name, self.last_name)
        path_save = pathlib.Path.cwd() / 'Profiles' / character_name
        pickle.dump(save_data, open(file=path_save.absolute().as_posix(), mode='wb'))
        terminal_output.print_text("Progress saved.")

    def search(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        if not kwargs['direct_object']:
            items_found = 0
            for hidden_item in self.room.hidden:
                if 100 - self.level >= hidden_item.visibility:
                    self.room.add_item(hidden_item)
                    self.room.remove_hidden_item(hidden_item)
                    terminal_output.print_text('You found {}!'.format(hidden_item.name))
                    items_found += 1
            if items_found == 0:
                terminal_output.print_text("There doesn't seem to be anything around here.")
            return
        else:
            for object in self.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.search(character=self)
                    return
            for item in self.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    terminal_output.print_text("Searching {} will not do you much good.".format(item.name))
                    return
            for char in self.room.enemies + self.room.npcs:
                if set(char.handle) & set(kwargs['direct_object']):
                    terminal_output.print_text("{} probably will not appreciate that.".format(char.first_name))
                    return
            else:
                terminal_output.print_text("That doesn't seem to be around here.")
                return

    def sell(self, **kwargs):
        """Determines if an item can be sold as well as calls the npc's sell function"""
        if self.check_round_time():
            return
        if self.is_dead():
            return
        elif not kwargs['direct_object']:
            terminal_output.print_text("What is it you are trying to sell?")
            return
        for npc in self.room.npcs:
            if set(npc.handle) & {kwargs['indirect_object']}:
                npc.sell_item(item=self.get_dominant_hand_inv())
                return
        else:
            terminal_output.print_text("Who are you trying to sell to?")

    def view_skills(self, **kwargs):
        terminal_output.print_text('''

Edged Weapons Base:  {}
        
Edged Weapons:    {}
Armor:            {}
Dodging:          {}
Perception:       {}
            '''.format(self.skills_base['edged_weapons'],
                       self.skills['edged_weapons'],
                       self.skills['armor'],
                       self.skills['dodging'],
                       self.skills['perception'])
              )

    def skin(self, **kwargs):
        if self.check_round_time():
            return
        if self.is_dead():
            return
        elif not kwargs['direct_object']:
            terminal_output.print_text("What are you trying to skin?")
            return
        else:
            for object in self.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.skin_corpse()
                    return
            for item in self.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    terminal_output.print_text("You can seem to find any way to skin {}.".format(item.name))
                    return
            for npc in self.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    terminal_output.print_text("You approach {}, but think better of it.".format(npc.name))
                    return

    def view_stats(self, **kwargs):
        terminal_output.print_text('''
Name:  {} {}
Level: {}
Strength:       {}          Intellect:   {}
Constitution:   {}          Wisdom:         {}
Dexterity:      {}          Logic:       {}
Agility:        {}          Spirit:         {}
        '''.format(self.first_name,
                   self.last_name,
                   self.level,
                   self.stats['strength'],
                   self.stats['intellect'],
                   self.stats['constitution'],
                   self.stats['wisdom'],
                   self.stats['dexterity'],
                   self.stats['logic'],
                   self.stats['agility'],
                   self.stats['spirit'])
              )

    def target_enemy(self, **kwargs):
        if not kwargs['direct_object']:
            terminal_output.print_text("What do you want to target?")
            return
        else:
            self.target = kwargs['direct_object']
            terminal_output.print_text("You are now targeting {}".format(self.target[0]))
            return






