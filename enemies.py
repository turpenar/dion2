
"""
This module contains enemy classes. Each enemy will operate on its own thread.
"""


import threading as threading
import time as time
import textwrap as textwrap
import random as random

import mixins as mixins
import combat as combat
import objects as objects
import world as world

def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal

class Enemy(mixins.ReprMixin, mixins.DataFileMixin, threading.Thread):
    def __init__(self, enemy_name: str, target: object, room: object, location_x: int, location_y: int, area: str, **kwargs):
        super(Enemy, self).__init__()

        self.enemy_data = self.get_enemy_by_name(enemy_name)

        self.name = self.enemy_data['name']
        self.description = self.enemy_data['description']
        self.handle = self.enemy_data['handle']
        self.adjectives = self.enemy_data['adjectives']
        self.level = self.enemy_data['level']
        self.health = self.enemy_data['health']
        self.strength = self.enemy_data['strength']
        self.constitution = self.enemy_data['constitution']
        self.spirit = self.enemy_data['spirit']
        self.mana = self.enemy_data['mana']
        self.dexterity = self.enemy_data['dexterity']
        self.defense = self.enemy_data['defense']
        self.spawn_location = self.enemy_data['spawn_location']

        self.location_x = location_x
        self.location_y = location_y
        self.area = area
        self.room = room

        self.target = target

        if self.room == target.room:
            for line in textwrap.wrap(self.enemy_data['entrance_text'], 80):
                terminal_output.print_text(line)

        self.right_hand_inv = self.enemy_data['right_hand']
        self.left_hand_inv = self.enemy_data['left_hand']

    def move(self, dx, dy):
        self.room.remove_enemy(self)
        if self.room == self.target.room:
            terminal_output.print_text(self.enemy_data['move_out_text'])
        self.location_x += dx
        self.location_y += dy
        self.room = world.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.add_enemy(self)
        if self.room == self.target.room:
            terminal_output.print_text(self.enemy_data['move_in_text'])

    def move_north(self, **kwargs):
        self.move(dx=0, dy=-1)

    def move_south(self, **kwargs):
        self.move(dx=0, dy=1)

    def move_east(self, **kwargs):
        self.move(dx=1, dy=0)

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)

    def is_alive(self):
        return self.health > 0

    def is_dead(self):
        terminal_output.print_text(self.enemy_data['death_text'])
        if self in self.room.enemies:
            self.room.remove_enemy(self)
        self.room.add_object(objects.Corpse(object_name=self.enemy_data['corpse'], room=self.room))
        self.target = None
        self.room = None

    def run(self):
        if self.room == self.target.room:
            terminal_output.print_text(self.enemy_data['move_in_text'])
        while self.health > 0:
            time.sleep(self.enemy_data['round_time'])
            if self.health <= 0:
                break
            elif (self.room == self.target.room) and (self.target.health > 0):
                combat.do_physical_damage_to_character(self, self.target)
            else:
                available_actions = self.room.adjacent_moves_enemy(area=self.area)
                action = random.choice(available_actions)
                action_method = getattr(self, action.method.__name__)
                action_method()
        return

    def view_description(self):
        return self.description





