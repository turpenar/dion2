
"""


TODO: Insert player name in combat text
"""


import random as random
import threading as threading
import config as config

import items as items

lock = threading.Lock()

def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal
    
def calculate_attack_strength(character):
    attack_strength = character.get_attack_strength_base()
    if character.get_dominant_hand_inv():
        if character.get_dominant_hand_inv().category == 'weapon':
            attack_strength += character.get_skill_bonus(character.get_dominant_hand_inv().sub_category)  
    return attack_strength

def calculate_defense_strength(character):
    weapon_ranks = 0
    if character.get_dominant_hand_inv():
        if character.get_dominant_hand_inv().category == 'weapon':
            weapon_ranks = chracter.get_skill(chracter.get_dominant_hand_inv().sub_category)
    defense_strength_evade = int(character.get_defense_strength_evade_base() + character.get_skill('dodging'))
    defense_strength_block = int(character.get_defense_strength_block_base() + character.get_skill('shield'))
    defense_strength_parry = int(character.get_defense_strength_parry_base() + weapon_ranks)
    return defense_strength_evade + defense_strength_block + defense_strength_parry

def success(strength, defense, att_random):
    return int((strength - defense + att_random - 100))

def damage(success, constitution):
    return int(success / constitution)

def melee_attack(self, target):
    attack_strength = calculate_attack_strength(self)

    with lock:
        att_random = random.randint(0,100)
        att_success = success(attack_strength, target.defense, att_random)
        att_damage = damage(att_success, self.get_stat('constitution'))

        terminal_output.print_text("""\
{} attacks {}!
STR {} - DEF {} + RAND {} - 100 = {}\
        """.format(self.name, target.name, attack_strength, target.defense, att_random, att_success))

        if att_damage < 0:
            terminal_output.print_text("""\
{} evades the attack.\
                """.format(target.name))
        else:
            target.health = target.health - att_damage
            terminal_output.print_text("""\
{} damages {} by {}.\
                """.format(self.name, target.name, att_damage))
            if target.health <= 0:
                target.is_dead()
                # self.experience += get_experience(character_level=self.level, target_level=target.level)
        return target

def do_physical_damage_to_character(self, character):
    if isinstance(self.right_hand_inv, items.Weapon):
        attack_modifier = self.right_hand_inv.attack_modifier
    else:
        attack_modifier = 0

    with lock:
        att_random = random.randint(0,100)
        att_success = success(self.strength, calculate_defense_strength(character), att_random)
        att_damage = damage(att_success, self.constitution)

        terminal_output.print_text("""\
{} attacks {}!
STR {} - DEF {} + RAND {} - 100 = {}\
        """.format(self.name, character.name, self.strength, calculate_defense_strength(character), att_random, att_success))

        if att_damage < 0:
            terminal_output.print_text("""\
{} evades the attack.\
                """.format(character.name))
        else:
            character.health = character.health - att_damage
            terminal_output.print_text("""\
{} damages {} by {}.\
                """.format(self.name, character.name, att_damage))
            if character.health <= 0:
                character.is_dead()
        return character



