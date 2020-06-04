
"""
This module contains enemy classes. Each enemy will operate on its own thread.

TODO:  Add ability to drop weapons and armor
"""


import threading as threading
import time as time
import textwrap as textwrap
import random as random

import mixins as mixins
import combat as combat
import objects as objects
import world as world

lock = threading.Lock()

def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal

class Enemy(mixins.ReprMixin, mixins.DataFileMixin, threading.Thread):
    def __init__(self, enemy_name: str, target: object, room: object, location_x: int, location_y: int, area: str, **kwargs):
        super(Enemy, self).__init__()

        self._enemy_data = self.get_enemy_by_name(enemy_name)

        self._name = self._enemy_data['name']
        self._description = self._enemy_data['description']
        self._handle = self._enemy_data['handle']
        self._adjectives = self._enemy_data['adjectives']
        self._category = self._enemy_data['category']
        self._level = self._enemy_data['level']
        self._health = self._enemy_data['health']
        self._health_max = self._enemy_data['health_max']
        self._attack_strength_base = self._enemy_data['attack_strength_base']
        self._defense_strength_base = self._enemy_data['defense_strength_base']
        self._weapon = self._enemy_data['weapon']
        self._armor = self._enemy_data['armor']
        self.spawn_location = self._enemy_data['spawn_location']

        self.location_x = location_x
        self.location_y = location_y
        self.area = area
        self.room = room

        self.target = target

        if self.room == target.room:
            for line in textwrap.wrap(self.enemy_data['entrance_text'], 80):
                terminal_output.print_text(line)

        self.right_hand_inv = self._enemy_data['right_hand']
        self.left_hand_inv = self._enemy_data['left_hand']

    def move(self, dx, dy):
        self.room.remove_enemy(self)
        if self.room == self.target.room:
            terminal_output.print_text(self._enemy_data['move_out_text'])
        self.location_x += dx
        self.location_y += dy
        self.room = world.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.add_enemy(self)
        if self.room == self.target.room:
            terminal_output.print_text(self._enemy_data['move_in_text'])

    def move_north(self, **kwargs):
        self.move(dx=0, dy=-1)

    def move_south(self, **kwargs):
        self.move(dx=0, dy=1)

    def move_east(self, **kwargs):
        self.move(dx=1, dy=0)

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)
        
    @property
    def name(self):
        with lock:
            return self._name
        
    @property
    def descriptionn(self):
        with lock:
            return self._description
        
    @property
    def handle(self):
        with lock:
            return self._handle
        
    @property
    def adjectives(self):
        with lock:
            return self._adjectives
        
    @property
    def category(self):
        with lock:
            return self._category
        
    @property
    def level(self):
        with lock:
            return self._level
        
    @property
    def health(self):
        with lock:
            return self._health
        
    @health.setter
    def health(self, health):
        with lock:
            self._health =  health
    
    @property    
    def health_max(self):
        with lock:
            return self._health_max
        
    @property
    def attack_strength_base(self):
        with lock:
            return self._attack_strength_base
        
    @property
    def defense_strength_base(self):
        with lock:
            return self._defense_strength_base
        
    @property
    def weapon(self):
        with lock:
            return self._weapon
        
    @weapon.setter
    def weapon(self, weapon):
        with lock:
            self._weapon = weapon
    
    @property
    def armor(self):
        with lock:
            return self._armor
        
    @armor.setter
    def armor(self, armor):
        with lock:
            self._armor = armor

    def is_alive(self):
        return self.health > 0

    def is_dead(self):
        terminal_output.print_text(self._enemy_data['death_text'])
        if self in self.room.enemies:
            self.room.remove_enemy(self)
        self.room.add_object(objects.Corpse(object_name=self.enemy_data['corpse'], room=self.room))
        self.target = None
        self.room = None

    def run(self):
        if self.room == self.target.room:
            terminal_output.print_text(self._enemy_data['move_in_text'])
        while self.health > 0:
            time.sleep(self._enemy_data['round_time'])
            if self.health <= 0:
                break
            elif (self.room == self.target.room) and (self.target.health > 0):
                combat.melee_attack_character(self, self.target)
            else:
                available_actions = self.room.adjacent_moves_enemy(area=self.area)
                action = random.choice(available_actions)
                action_method = getattr(self, action.method.__name__)
                action_method()
        return

    def view_description(self):
        return self.description





