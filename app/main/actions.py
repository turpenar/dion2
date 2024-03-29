"""


TODO: Exit out of all demon programs when quit
TODO: Check the characters position before it moves or performs certain actions.
TODO: Integrate the BUY function into the shops.

"""

import pathlib as pathlib
import textwrap as textwrap

from app.main import world, enemies, command_parser, config, npcs, combat, events


verbs = config.verbs
stances = config.stances
action_history = []
wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)


def do_action(action_input, character=None):
    action_history.insert(0,action_input)
    if not character:
        events.game_event(game_event_text="No character loaded. You will need to create a new character or load an existing character.")
        return
    if len(action_input) == 0:
        events.game_event("")
        return
    kwargs = command_parser.parser(action_input)
    return DoActions.do_action(kwargs['action_verb'], character, **kwargs).action_result


class DoActions:
    def __init__(self, character, **kwargs):
        self.character = character
        self.action_result = {"room_change": {"room_change_flag":  False,
                                              "old_room":  None,
                                              "new_room":  None},
                              "character_output":  None,
                              "room_output":  {},
                              "area_output":  None,
                              "status_window":  None}

    do_actions = {}

    @classmethod
    def register_subclass(cls, action):
        """Catalogues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.do_actions[action] = subclass
            return subclass
        return decorator

    @classmethod
    def do_action(cls, action, character, **kwargs):
        """Method used to initiate an action"""
        if action not in cls.do_actions:
            events.game_event("I am sorry, I did not understand.")
            return
        return cls.do_actions[action](character, **kwargs)
    
    def update_room(self, old_room_number, new_room_number):
        self.action_result['room_change']['room_change_flag'] = True
        self.action_result['room_change']['old_room'] = old_room_number
        self.action_result['room_change']['new_room'] = new_room_number
        return
    
    def update_character_output(self, character_output_text):
        self.action_result['character_output'] = character_output_text
        
    def update_room_output(self, room_output_text):
        self.action_result['room_output'] = room_output_text
        
    def update_area_output(self, area_output_text):
        self.action_result['area_output'] = area_output_text
    
    def update_status(self, status_text):
        self.action_result['status_window'] = status_text
        


@DoActions.register_subclass('ask')
class Ask(DoActions):
    """\
    Certain npcs have information that is valuable for you. The ASK verb allows you to interact with these npcs
    and obtain that information.

    Usage:
    ASK <npc> about <subject>\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("Who are you trying to ask?")
            return
        elif not kwargs['indirect_object']:
            events.game_event("What are you trying to ask about?")
            return
        else:
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    npc.ask_about(object=kwargs['indirect_object'])
                    return
            else:
                events.game_event("That doesn't seem to do any good.")


@DoActions.register_subclass('attack')
class Attack(DoActions):
    """\
    ATTACK allows you to engage in combat with an enemy. Provided you are not in round time, ATTACK swings
    the weapon in your right hand (or your bare fist if there is no weapon) at the enemy. You will not be able
    to attack anyone other than enemies.

    Usage:
    ATTACK <enemy> : Engages an enemy and begins combat.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if kwargs['direct_object']:
            character.target = kwargs['direct_object']
        if not character.target:
            events.game_event("Who are you going to attack? You do not have a target.")
            return
        else:
            for npc in character.room.npcs:
                if set(npc.handle) & set(character.target):
                    events.game_event("{} will probably not appreciate that.".format(npc.name))
                    return
            enemy_found = False
            for enemy in character.room.enemies:
                if set(enemy.handle) & set(character.target):
                    enemy_found = True
                    combat.melee_attack_enemy(character, enemy)
                    return
            if not enemy_found:
                events.game_event("{} is not around here.".format(kwargs['direct_object']))
                return
            
        
@DoActions.register_subclass('attribute')
class Attributes(DoActions):
    """\
    ATTRIBUTES allows you to view various attributes\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        events.game_event('''
Attribute:  {}
            '''.format(character.attack_strength_base))
        
        
@DoActions.register_subclass('buy')
class Buy(DoActions):
    """\
    BUY enables you to purchase an item from a shop.
    
    Usage:
    
    BUY <#>:  Finalize purchase of the selected item.\
    """
    
    def __init__(self, character, **kwargs):
         
        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return 
            
        if character.room.is_shop == False:
            events.game_event("You can't seem to find a way to order anything here.")
            return
        if character.room.shop_filled == False:
            events.game_event("You will need to ORDER first.")
            return
        if character.room.shop.in_shop == False:
            events.game_event("You have exited the shop. You will need to ORDER again.")
            return 
        if character.get_dominant_hand_inv() is not None:
            events.game_event("You will need to empty your right hand first.")
            return
        character.set_dominant_hand_inv(character.room.shop.buy_item(number=kwargs['number_1']))


@DoActions.register_subclass('drop')
class Drop(DoActions):
    """\
    DROP sets an object within your environment. This verb works the same as PUT <item>.

    Usage:
    DROP <item> : Places an item within an environment.
    DROP <item> in <object/item> : Will put an item within an object or within another item if that object or item
    is a container and if that object or item has enough room within it.
    DROP <item> on <object/item> : Will put an item on top of an object or on top of another item if that object
    or item is stackable.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("I'm sorry, I could not understand what you wanted.")
            return
        elif character.get_dominant_hand_inv() is None:
            events.game_event("You do not have that item in your hand")
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            events.game_event("You do not have that item in your right hand.")
            return
        else:
            character.room.items.append(character.get_dominant_hand_inv())
            events.game_event("You drop " + character.get_dominant_hand_inv().name)
            character.set_dominant_hand_inv(item=None)
            character.print_status()
            return


@DoActions.register_subclass('east')
@DoActions.register_subclass('e')
class East(DoActions):
    """\
    Moves you east, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)     
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if world.tile_exists(x=self.character.location_x + 1, y=self.character.location_y, area=self.character.area):
            if character.room.shop_filled == True:
                if character.room.shop.in_shop == True:
                    character.room.shop.exit_shop()
            old_room = self.character.room.room_number             
            self.character.move_east()
            self.update_room(old_room_number=old_room, new_room_number=self.character.room.room_number)
            self.update_status(character.get_status())
            return
        else:
            events.game_event("You cannot find a way to move in that direction.")
            return
            
            
@DoActions.register_subclass('exit')
class Exit(DoActions):
    """\
    When ordering in a shop, EXIT leaves the order menu. In order to see the menu again, you will need to ORDER again.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.room.is_shop == False:
            game_window.print_status("You have nothing to exit.")
            return 
        if character.room.shop_filled == False:
            game_window.print_status("You have nothing to exit.")
            return
        if character.room.shop.in_shop == False:
            game_window.print_status("You have nothing to exit.")
            return            
        else:
            character.room.shop.exit_shop()
            character.print_status()
            return

            
@DoActions.register_subclass('experience')
@DoActions.register_subclass('exp')
class Experience(DoActions):
    """\
    Displays your experience information.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        events.game_event('''\
Experience:  {}
        '''.format(character.experience))


@DoActions.register_subclass('flee')
class Flee(DoActions):
    """\
    FLEE sends you in a random direction in your environment. FLEE can only be used when not in round time.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)       

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if character.room.shop_filled == True:
            if character.room.shop.in_shop == True:
                character.room.shop.exit_shop()
        available_moves = character.room.adjacent_moves()
        r = random.randint(0, len(available_moves) - 1)
        actions.do_action(action_input=available_moves[r], character=character)
        character.print_status()

        return


@DoActions.register_subclass('get')
@DoActions.register_subclass('take')
class Get(DoActions):
    """\
    GET retrieves an item from your surroundings. Many objects cannot be moved from their current position.
    The item will be taken by your right hand, therefore you right hand will need to be empty. This
    verb functions the same as TAKE.

    Usage:
    GET <item>\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not kwargs['direct_object']:
            events.game_event("I'm sorry, I could not understand what you wanted.")
            return
        for room_object in character.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                events.game_event("Perhaps picking up {} is not a good idea.".format(room_object.name))
                return
        if character.get_dominant_hand_inv() is None:
            item_found = False
            for room_item in character.room.items:
                if set(room_item.handle) & set(kwargs['direct_object']):
                    character.set_dominant_hand_inv(room_item)
                    character.room.items.remove(room_item)
                    events.game_event("You pick up {}.".format(room_item.name))
                    character.print_status()
                    return
            if not item_found:
                for inv_item in character.inventory:
                    if inv_item.container:
                        for sub_item in inv_item.items:
                            if set(sub_item.handle) & set(kwargs['direct_object']):
                                character.set_dominant_hand_inv(sub_item)
                                inv_item.items.remove(sub_item)
                                events.game_event("You take {} from {}.".format(sub_item.name, inv_item.name))
                                character.print_status()
                                return
            if not item_found:
                events.game_event("A " + kwargs['direct_object'][0] + " is nowhere to be found")
        else:
            events.game_event('You already have something in your right hand')


@DoActions.register_subclass('give')
class Give(DoActions):
    """\
    GIVE allows you to exchange items between you and various npcs. In order to give an item to an npc, you
    must have the item in your right hand.

    Usage:
    GIVE <item> to <npc> : Gives the item to the npc if the npc has the ability to accept the item.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("What are you trying to give?")
            return
        elif character.get_dominant_hand_inv() is None:
            events.game_event("You don't seem to be holding that item in your hand.")
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            events.game_event("You don't seem to be holding that item in your hand.")
            return
        elif not kwargs['indirect_object']:
            events.game_event("To whom do you want to give?")
            return
        else:
            for npc in character.room.npcs:
                if {npc.first_name.lower()} & set(kwargs['indirect_object']):
                    if npc.give_item(character.get_dominant_hand_inv()):
                        character.set_dominant_hand_inv(item=None)
                        character.print_status()
                        return
                    else:
                        return
            events.game_event("That didn't seem to work.")
            return


@DoActions.register_subclass('go')
class Go(DoActions):
    """\
    GO allows you to move toward a certain object. If the object can be passed through, you will pass through it.

    Usage:

    GO <object> : move toward or through an object.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if not kwargs['direct_object']:
            events.game_event("Go where?")
            return
        for room_object in character.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                events.game_event("You move toward {}.".format(room_object.name))
                room_object.go_object(character=character)
                return
        for room_item in character.room.items:
            if set(room_item.handle) & set(kwargs['direct_object']):
                events.game_event("You move toward {}.".format(room_item.name))
                return
        for room_npc in character.room.npcs:
            if set(room_npc.handle) & set(kwargs['direct_object']):
                events.game_event("You move toward {}.".format(room_npc.name))
                return
        
@DoActions.register_subclass('health')
class Health(DoActions):
    """\
    HEALTH shows your current health attributes.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        events.game_event('''
Health:  {} of {} hit points
            '''.format(character.health,
                       character.health_max))


@DoActions.register_subclass('help')
class Help(DoActions):
    """\
    Provides help on all parts of the game

    Usage:

    HELP <subject> : Output help on a specific subject.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        verb_list = ""

        if kwargs['subject_verb'] == None:
                    
            for a, b, c in zip(verbs[::3], verbs[1::3], verbs[2::3]):
                verb_list = verb_list + '{:30s}{:30s}{:30s}\n'.format(a,b,c)
            
            events.game_event("""
Below are the list of actions for which you can ask for help.
Type HELP <verb> for more information about that specific verb.
{}\
            """.format(verb_list))

            
        elif kwargs['subject_verb'] in DoActions.do_actions:
            events.game_event(DoActions.do_actions[kwargs['subject_verb']].__doc__)
        else:
            events.game_event("I'm sorry, what did you need help with?")
            
@DoActions.register_subclass('info')
@DoActions.register_subclass('information')
class Information(DoActions):
    """\
    Provides general information on your character including level, experience, and other attributes.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        events.game_event('''
Name:  {} {}
Gender:  {}
Race:  {}
Profession:  {}
Level:  {}
            '''.format(character.first_name, character.last_name,
                       character.gender,
                       character.race,
                       character.profession,
                       character.level))


@DoActions.register_subclass('inventory')
class Inventory(DoActions):
    """\
    INVENTORY allows you to view your inventory. It will list all items you have in your possession.  INVENTORY
    will not list the items within any containers you have.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.get_dominant_hand_inv():
            right_hand = "You have {} in your {} hand.".format(character.get_dominant_hand_inv().name, character.dominance)
        else:
            right_hand = "Your right hand is empty."
        if character.get_non_dominant_hand_inv():
            left_hand = "You have {} in your {} hand.".format(character.get_non_dominant_hand_inv().name, character.non_dominance)
        else:
            left_hand = "Your left hand is empty."
        inventory_clothing = [x.name for x in character.inventory if x.category == 'clothing']
        if len(inventory_clothing) > 1:
            inventory_clothing = "You are wearing {} and {}.".format(', '.join(inventory_clothing[:-1]), inventory_clothing[-1])
        elif len(inventory_clothing) == 1:
            inventory_clothing = "You are wearing {}.".format(inventory_clothing[0])
        else:
            inventory_clothing = "You are wearing nothing."
        
        inventory_armor = []  
        for category in character.armor:
            inventory_armor.append(character.armor[category])
        if len(inventory_armor) > 1:
            inventory_armor ="You are also wearing {} and {}.".format(character.object_pronoun, ', '.join(inventory_armor[:-1]), inventory_armor[-1])
        elif len(inventory_armor) == 1:
            inventory_armor = "You are also wearing {}.".format(inventory_armor[0].name)
        else:
            inventory_armor = "You are also wearing no armor.".format(character.object_pronoun)
        wealth = "You have {} gulden.".format(character.money)
        events.game_event('''\
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
        
        
@DoActions.register_subclass('kneel')
class Kneel(DoActions):
    """\
    Moves you to a kneeling position. While you may perform many actions from this position,
    movement is not possible.
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
    
        if character.check_round_time():
            return 
        if character.is_dead():
            return 
        if character.position == 'kneeling':
            events.game_event('You seem to already be kneeling.')
            character.print_status()
            return 
        else:
            character.position = 'kneeling'
            events.game_event('You move yourself to a kneeling position.')
            character.print_status()
            return
        
        
@DoActions.register_subclass('lie')
class Lie(DoActions):
    """\
    Moves you to a lying position on the ground. While many actions can be performed on the ground, 
    movement is not possible.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.check_round_time():
            return 
        if character.is_dead():
            return 
        if character.position == 'lying':
            events.game_event('You seem to already be lying down.')
            character.print_status()
            return 
        else:
            character.position = 'lying'
            events.game_event('You lower yourself to the ground and lie down.')
            character.print_status()
            return


@DoActions.register_subclass('look')
@DoActions.register_subclass('l')
class Look(DoActions):
    """\
    View the environment and objects or items within your environment.

    Usage:
    LOOK : shows the descriptions of the environment around you.
    LOOK <object/item> : shows the description of the object at which you want to look.
    LOOK <npc> : shows the description of the npc at which you want to look.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if kwargs['preposition'] == None:
            character.room.intro_text()
            return
        if kwargs['preposition'][0] == 'in':
            item_found = False
            if kwargs['indirect_object'] is None:
                events.game_event("I am not sure what you are referring to.")
                return
            for item in character.room.items + character.room.objects + character.room.npcs + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if isinstance(item, npcs.NPC):
                    events.game_event("It wouldn't be advisable to look in " + item.name)
                    return
                if set(item.handle) & set(kwargs['indirect_object']):
                    events.game_event(item.contents())
                    return
            if item_found is False:
                events.game_event("A {} is nowhere to be found.".format(kwargs['indirect_object'][0]))
                return
        if kwargs['preposition'][0] == 'at':
            item_found = False
            if kwargs['indirect_object'] is None:
                events.game_event("I am not sure what you are referring to.")
                return
            for item in character.room.items + character.room.objects + character.room.npcs + character.room.enemies + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if not item:
                    pass
                elif set(item.handle) & set(kwargs['indirect_object']):
                    item.view_description()
                    return
            for item in character.inventory:
                if set(item.handle) & set(kwargs['indirect_object']):
                    item.view_description()
                    return
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['indirect_object']):
                    object.view_description()
                    return
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['indirect_object']):
                    npc.view_description()
                    return
            for enemy in character.room.enemies:
                if set(npc.handle) & set(kwargs['indirect_object']):
                    enemy.view_description()
                    return
            if item_found is False:
                events.game_event("At what did you want to look?")
                return
        else:
            events.game_event("I'm sorry, I didn't understand you.")
            return


@DoActions.register_subclass('north')
@DoActions.register_subclass('n')
class North(DoActions):
    """\
    Moves you north, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)      
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if world.tile_exists(x=self.character.location_x, y=self.character.location_y - 1, area=self.character.area):
            if character.room.shop_filled == True:
                if character.room.shop.in_shop == True:
                    character.room.shop.exit_shop()        
            self.character.move_north()
            character.print_status()
            return
        else:
            events.game_event('You cannot find a way to move in that direction.')
            return
            
            
@DoActions.register_subclass('order')
class Order(DoActions):
    """\
    In certain rooms, you are able to order products through an ordering system. ORDER initiates the ordering system.\
    
    Usage:
    ORDER:  Enters the shop and displays the shop menu in the status window
    ORDER <#>:  Orders the relevant item. You cannot order a specific item until you have entered the shop using the ORDER command by itself.
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
         
        if character.check_round_time():
            return
        if character.is_dead():
            return
            
        if character.room.is_shop == False:
            events.game_event("You can't seem to find a way to order anything here.")
            return 
        elif character.room.is_shop == True:  
            if character.room.shop_filled == False:             
                character.room.fill_shop()
                character.room.shop.enter_shop()
                return
            if character.room.shop.in_shop == False:
                character.room.shop.enter_shop()
                return
            character.room.shop.order_item(kwargs['number_1'])
            return

                

@DoActions.register_subclass('position')
@DoActions.register_subclass('pos')
class Position(DoActions):
    """\
    Displays the position you are currently in.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character = character
        
        self.position()
        
    def position(self):
        events.game_event('''You are currently in the {} position.'''.format(self.character.position))


@DoActions.register_subclass('put')
class Put(DoActions):
    """\
    PUT sets an object within your environment.  This usage works the same as DROP <item>.

    Usage:
    PUT <item> : Places an item within an environment.
    PUT <item> in <object/item> : Will put an item within an object or within another item if that object or item
    is a container and if that object or item has enough room within it.
    PUT <item> on <object/item> : Will put an item on top of an object or on top of another item if that object
    or item is stackable.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not kwargs['direct_object']:
            events.game_event("What is it you're trying to put down?")
            return
        elif character.get_dominant_hand_inv() is None:
            events.game_event("You do not have that item in your hand.")
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            events.game_event("You do not have that item in your right hand.")
            return
        elif kwargs['preposition'][0] == "in":
            for inv_item in character.inventory:
                if set(inv_item.handle) & set(kwargs['indirect_object']):
                    if inv_item.container == False:
                        events.game_event("{} won't fit in there.".format(character.get_dominant_hand_inv().name))
                        return
                    if len(inv_item.items) == inv_item.capacity:
                        events.game_event("{} can't hold any more items".format(inv_item.name))
                        return
                    inv_item.items.append(character.get_dominant_hand_inv())
                    events.game_event("You put {} {} {}".format(character.get_dominant_hand_inv().name, kwargs['preposition'][0], inv_item.name))
                    character.set_dominant_hand_inv(item=None)
                    character.print_status()
                    return
            for room_item in character.room.items:
                if set(room_item.handle) & set(kwargs['indirect_object']):
                    if room_item.container == False:
                        events.game_event("{} won't fit {} there.".format(character.right_hand_inv[0].name, kwargs['preposition'][0]))
                        return
                    room_item.items.append(character.get_dominant_hand_inv())
                    character.set_dominant_hand_inv(item=None)
                    events.game_event("You put {} {} {}".format(character.get_dominant_hand_inv().name, kwargs['preposition'][0], room_item.name))
                    character.set_dominant_hand_inv(item=None)
                    character.print_status()
                    return
        elif kwargs['preposition'][0] == "on":
            events.game_event("You cannot stack items yet.")
            return
        else:
            events.game_event("That item is not around here, unfortunately.")
            return


@DoActions.register_subclass('quit')
class Quit(DoActions):
    """\
    Exits the game.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        events.game_event("You will need to find a way to exit the game.")


@DoActions.register_subclass('save')
class Save(DoActions):
    """\
    \
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.save()


@DoActions.register_subclass('search')
class Search(DoActions):
    """\
    SEARCH allows you to explore your environment if the object, enemy, or area can be explored.

    Usage:
    SEARCH : Searches the environment around you and uncovers hidden items or objects.
    SEARCH <enemy> : Searches an enemy, uncovers any potential items that the enemy could be hiding, and places
    them in your environment.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not kwargs['direct_object']:
            items_found = 0
            for hidden_item in character.room.hidden:
                if 100 - character.level >= hidden_item.visibility:
                    character.room.add_item(hidden_item)
                    character.room.remove_hidden_item(hidden_item)
                    events.game_event('You found {}!'.format(hidden_item.name))
                    items_found += 1
            if items_found == 0:
                events.game_event("There doesn't seem to be anything around here.")
            return
        else:
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.search(character=character)
                    return
            for item in character.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    events.game_event("Searching {} will not do you much good.".format(item.name))
                    return
            for char in character.room.enemies + character.room.npcs:
                if set(char.handle) & set(kwargs['direct_object']):
                    events.game_event("{} probably will not appreciate that.".format(char.first_name))
                    return
            else:
                events.game_event("That doesn't seem to be around here.")
                return


@DoActions.register_subclass('sell')
class Sell(DoActions):
    """\
    SELL allows you to exchange items for gulden. Certain merchants look for items you may find in the wilds.
    Different merchants look for different items. The item must be in your right hand.

    Usage:
    SELL <item> to <npc>  : Exchanges items for gulden with an npc if an item can be exchanged.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("What is it you are trying to sell?")
            return
        for npc in character.room.npcs:
            if set(npc.handle) & {kwargs['indirect_object']}:
                npc.sell_item(item=character.get_dominant_hand_inv())
                return
        else:
            events.game_event("Who are you trying to sell to?")
        
        
@DoActions.register_subclass('sit')
class Sit(DoActions):
    """\
    Moves you to a sitting position. While you can perform many actions while in a sitting position,
    movement is no possible.
    """        
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return 
        if character.is_dead():
            return 
        if character.position == 'sitting':
            events.game_event('You seem to already be sitting.')
            character.print_status()
            return 
        else:
            character.position = 'sitting'
            events.game_event('You move yourself to a sitting position.')
            character.print_status()
            return


@DoActions.register_subclass('skills')
class Skills(DoActions):
    """\
    SKILLS displays the skills available to you as well as the skill rating for your character. Different skills
    allow you to accomplish different tasks.

    Usage:
    SKILLS:  Shows your available skills and their rating.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        events.game_event('''
Edged Weapons Base:  {}
        
Edged Weapons:    {}  ({})          Armor:              {}  ({})
Blunt Weapons:    {}  ({})          Shield:             {}  ({})
Polearm Weapons:  {}  ({})          Dodging:            {}  ({})
Thrown Weapons:   {}  ({})          Physical Fitness:   {}  ({})
Ranged Weapons:   {}  ({})          Perception:         {}  ({})

            '''.format(character.skills_base['edged_weapons'], 
                       character.skills['edged_weapons'], character.skills_bonus['edged_weapons'],
                       character.skills['armor'], character.skills_bonus['armor'],
                       character.skills['blunt_weapons'], character.skills_bonus['blunt_weapons'],
                       character.skills['shield'], character.skills_bonus['shield'],
                       character.skills['polearm_weapons'], character.skills_bonus['polearm_weapons'],
                       character.skills['dodging'], character.skills_bonus['dodging'],
                       character.skills['thrown_weapons'], character.skills_bonus['thrown_weapons'],
                       character.skills['physical_fitness'], character.skills_bonus['physical_fitness'],
                       character.skills['ranged_weapons'], character.skills_bonus['ranged_weapons'],
                       character.skills['perception'], character.skills_bonus['perception'])
              )


@DoActions.register_subclass('skin')
class Skin(DoActions):
    """\
    Many enemies are able to be skinned for various pelts, hides, etc. The SKIN verb allows you to skin enemies.
    if successful the resulting item will be places within the environment. Not all enemies are able to be skinned.

    Usage:
    SKIN <enemy> : Skins an enemy and, if successful, leaves a skin.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("What are you trying to skin?")
            return
        else:
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.skin_corpse()
                    return
            for item in character.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    events.game_event("You can seem to find any way to skin {}.".format(item.name))
                    return
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    events.game_event("You approach {}, but think better of it.".format(npc.name))
                    return


@DoActions.register_subclass('south')
@DoActions.register_subclass('s')
class South(DoActions):
    """\
    Moves you south, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)        
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if world.tile_exists(x=self.character.location_x, y=self.character.location_y + 1, area=self.character.area):
            if character.room.shop_filled == True:
                if character.room.shop.in_shop == True:
                    character.room.shop.exit_shop()        
            self.character.move_south()
            character.print_status()        
        else:
            events.game_event("You cannot find a way to move in that direction.")
            
            
@DoActions.register_subclass('stance')
class Stance(DoActions):
    """\
    STANCE controls the position in which you carry yourself in combat. Your stance will affect the amount of 
    attack and defensive strength you have during combat.
    
    Usage:
    STANCE:  Shows your current stance.
    STANCE <type>: Changes your stance to the desired stance.
    
    Types of Stances:
    offensive
    forward
    neutral
    guarded
    defense\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character = character
        
        self.stance(character=character, desired_stance=kwargs['adjective_1'])
        
    def stance(self, character, desired_stance):
        if not desired_stance:
            events.game_event('''You are currently in the {} stance.'''.format(self.character.stance))
            return
        if set(desired_stance) & set(stances):
            self.character.stance = desired_stance[0]
            events.game_event('''You are now in {} stance.'''.format(desired_stance[0]))
            character.print_status()
            return
        else:
            events.game_event("You cannot form that stance.")
            return


@DoActions.register_subclass('stand')
class Stand(DoActions):
    """\
    Raises you to the standing position if you are not already in the standing position.
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character = character
        
        self.stand(character=self.character)
        
    def stand(self, character):
        if self.character.check_round_time():
            return 
        if self.character.is_dead():
            return 
        if self.character.position == 'standing':
            self.update_character_output(character_output_text="You seem to already be standing.")
            self.update_status(status_text=character.get_status())
            return 
        else:
            self.character.position = 'standing'
            self.update_character_output(character_output_text="You raise yourself to a standing position.")
            self.update_room_output(room_output_text={character.room.room_number: "{} raises {}self to a standing position".format(character.first_name, character.possessive_pronoun)})
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('stats')
class Stats(DoActions):
    """\
    Displays your general statistics.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        events.game_event('''
Name:  {} {}
Level: {}
Strength:       {}  ({})        Intellect:      {}  ({})
Constitution:   {}  ({})        Wisdom:         {}  ({})
Dexterity:      {}  ({})        Logic:          {}  ({})
Agility:        {}  ({})        Spirit:         {}  ({})
        '''.format(character.first_name,
                   character.last_name,
                   character.level,
                   character.stats['strength'], character.stats_bonus['strength'],
                   character.stats['intellect'], character.stats_bonus['intellect'],
                   character.stats['constitution'], character.stats_bonus['constitution'],
                   character.stats['wisdom'], character.stats_bonus['wisdom'],
                   character.stats['dexterity'], character.stats_bonus['dexterity'],
                   character.stats['logic'], character.stats_bonus['logic'],
                   character.stats['agility'], character.stats_bonus['agility'],
                   character.stats['spirit'], character.stats_bonus['spirit'])
              )




@DoActions.register_subclass('target')
class Target(DoActions):
    """\
    When in combat, you must TARGET an enemy before you can ATTACK them. Use the TARGET verb to set the enemy
    for which you want to ATTACK. TARGET only needs to be set once for the duration of the combat. The enemy
    does not have to be within sight in order for you to TARGET it.

    Usage:
    TARGET <enemy> : Targets an enemy.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if not kwargs['direct_object']:
            events.game_event("What do you want to target?")
            return
        else:
            character.target = kwargs['direct_object']
            events.game_event("You are now targeting {}".format(self.target[0]))
            return
        

@DoActions.register_subclass('west')
@DoActions.register_subclass('w')
class West(DoActions):
    """\
    Moves you west, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)       
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not character.check_position_to_move():
            return
        if world.tile_exists(x=self.character.location_x - 1, y=self.character.location_y, area=self.character.area):
            if character.room.shop_filled == True:
                if character.room.shop.in_shop == True:
                    character.room.shop.exit_shop()        
            self.character.move_west()
            character.print_status()
        else:
            events.game_event("You cannot find a way to move in that direction.")


class Action:
    def __init__(self, method, name, action, **kwargs):
        self.method = method
        self.name = name
        self.action = action
        self.kwargs = kwargs

    def __str__(self):
        return "{}: {}".format(self.action, self.name)


class MoveNorthEnemy(Action):
    def __init__(self, **kwargs):
        super().__init__(method=enemies.Enemy.move_north,
                         name='Move North',
                         action=['north'],
                         kwargs=kwargs)


class MoveSouthEnemy(Action):
    def __init__(self, **kwargs):
        super().__init__(method=enemies.Enemy.move_south,
                         name='Move South',
                         action=['south'],
                         kwargs=kwargs)


class MoveEastEnemy(Action):
    def __init__(self, **kwargs):
        super().__init__(method=enemies.Enemy.move_east,
                         name='Move East',
                         action=['east'],
                         kwargs=kwargs)


class MoveWestEnemy(Action):
    def __init__(self, **kwargs):
        super().__init__(method=enemies.Enemy.move_west,
                         name='Move West',
                         action=['west'],
                         kwargs=kwargs)

