
"""


TODO: Insert player name in combat text
"""


import random as random
import threading as threading
import config as config

import items as items

lock = threading.Lock()

weapon_damage_factors = config.WEAPON_DAMAGE_FACTORS

def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal
    
def calculate_attack_strength(character, weapon):
    attack_strength = character.attack_strength_base
    if character.category == "player":
        if weapon:
            if weapon.category == 'weapon':
                attack_strength += character.skills_bonus[weapon.sub_category] 
    return attack_strength
    
def calculate_defense_strength_evade(character):
    defense_strength_evade = int(character.defense_strength_evade_base + character.skills['dodging'])
    return defense_strength_evade
    
def calculate_defense_strength_block(character):
    defense_strength_block = int(character.defense_strength_block_base) + character.skills['shield']
    return defense_strength_block
        
def calculate_defense_strength_parry(character, weapon):
    defense_strength_parry = int(character.defense_strength_parry_base + character.skills['dodging'])      
    if weapon:
        if weapon.category == 'weapon':
            weapon_ranks = character.skills[character.get_dominant_hand_inv().sub_category]
            defense_strength_parry += int(weapon_ranks)
            return defense_strength_parry
        else:
            return defense_strength_parry

def calculate_defense_strength(character, weapon):
    defense_strength = 0
    if character.category == "player":
        defense_strength_evade = calculate_defense_strength_evade(character=character)
        defense_strength_block = calculate_defense_strength_block(character=character)
        defense_strength_parry = calculate_defense_strength_parry(character=character, weapon=weapon)  
        defense_strength =  defense_strength_evade + defense_strength_block + defense_strength_parry
    else:
        defense_strength = character.defense_strength_base
    return defense_strength

def end_roll(attack, defense, random):
    return int((attack - defense + random))

def get_damage(end_roll, weapon, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    try:
        if weapon.category == 'weapon':
            weapon_classification = weapon.classification
    except:
        weapon_classification = "None"
        
    damage_factor = weapon_damage_factors.loc[weapon_classification, armor_classification]
    return int(round((end_roll - 100) * damage_factor))

def melee_attack_enemy(self, target):
    attack_strength = calculate_attack_strength(self, self.get_dominant_hand_inv())
    defense_strength = calculate_defense_strength(character=target, weapon=target.weapon)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, random=att_random)
    round_time = self.set_round_time(3)
    
    result = None
    if att_end_roll <= 100:
        result = """\
{} evades the attack.
Round time:  {} seconds
            """.format(target.name, round_time)
    else:
        att_damage = get_damage(att_end_roll, self.get_dominant_hand_inv(), target.armor)
        target.health = target.health - att_damage
        death_text = target.is_killed()
        result = """\
{} damages {} by {}.
Round time:  {} seconds
{}\
            """.format(self.name, target.name, att_damage, death_text, round_time)

    terminal_output.print_text("""\
{} attacks {}!
STR {} - DEF {} + D100 ROLL {} = {}
{}\
    """.format(self.name, target.name, attack_strength, defense_strength, att_random, att_end_roll, result))
    return target

def melee_attack_character(self, character):
    attack_strength = calculate_attack_strength(self, self.weapon)
    defense_strength = calculate_defense_strength(character=character, weapon=character.get_dominant_hand_inv())
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength,defense=defense_strength, random=att_random)

    result = None
    death_text = None
    if att_end_roll <= 100:
        result = """\
{} evades the attack.\
            """.format(character.name)
    else:
        att_damage = get_damage(att_end_roll, self.weapon, character.armor)
        character.health = character.health - att_damage
        death_text = character.is_killed()
        result = """\
{} damages {} by {}.
{}\
            """.format(self.name, character.name, att_damage, death_text)

    terminal_output.print_text("""\
{} attacks {}!
STR {} - DEF {} + D100 ROLL {} = {}
{}\
    """.format(self.name, character.name, attack_strength, defense_strength, att_random, att_end_roll, result))

    return character




