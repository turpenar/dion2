"""


TODO: Exit out of all demon programs when quit

"""

import pathlib as pathlib

import world as world
import enemies as enemies
import command_parser as command_parser
import config as config


verbs = config.verbs
action_history = []


def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal


def do_action(action_input, character):
    action_history.insert(0,action_input)
    print(action_history)
    if len(action_input) == 0:
        terminal_output.print_text("")
        return
    kwargs = command_parser.parser(action_input)
    DoActions.do_action(kwargs['action_verb'], character, **kwargs)


class DoActions:
    def __init__(self, character, **kwargs):
        self.character = character

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
            terminal_output.print_text("I am sorry, I did not understand.")
            return
        return cls.do_actions[action](character, **kwargs)


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

        self.character.ask(**kwargs)


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

        self.character.attack(**kwargs)
        
        
@DoActions.register_subclass('attribute')
class Attributes(DoActions):
    """\
    ATTRIBUTES allows you to view various attributes\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.view_attributes(**kwargs)


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

        self.character.put(**kwargs)


@DoActions.register_subclass('east')
@DoActions.register_subclass('e')
class East(DoActions):
    """\
    Moves you east, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if world.tile_exists(x=self.character.location_x + 1, y=self.character.location_y, area=self.character.area):
            self.character.move_east()
        else:
            terminal_output.print_text("You cannot find a way to move in that direction.")
            
@DoActions.register_subclass('experience')
@DoActions.register_subclass('exp')
class Experience(DoActions):
    """\
    Displays your experience information.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character.view_experience()


@DoActions.register_subclass('flee')
class Flee(DoActions):
    """\
    FLEE sends you in a random direction in your environment. FLEE can only be used when not in round time.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.flee(**kwargs)


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

        self.character.get(**kwargs)


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

        self.character.give(**kwargs)


@DoActions.register_subclass('go')
class Go(DoActions):
    """\
    GO allows you to move toward a certain object. If the object can be passed through, you will pass through it.

    Usage:

    GO <object> : move toward or through an object.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.go(**kwargs)
        
@DoActions.register_subclass('health')
class Health(DoActions):
    """\
    HEALTH shows your current health attributes.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character.view_health(**kwargs)


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
        
        for a, b, c in zip(verbs[::3], verbs[1::3], verbs[2::3]):
            verb_list = verb_list + '{:<30}{:<30}{:<}\n'.format(a,b,c)

        if kwargs['subject_verb'] == None:
            terminal_output.print_text("""
Below are the list of actions with which you can ask for help.
Type HELP <verb> for more information about that specific verb.
{}\
            """.format(verb_list))

            
        elif kwargs['subject_verb'] in DoActions.do_actions:
            terminal_output.print_text(DoActions.do_actions[kwargs['subject_verb']].__doc__)
        else:
            terminal_output.print_text("I'm sorry, what did you need help with?")
            
@DoActions.register_subclass('info')
@DoActions.register_subclass('information')
class Information(DoActions):
    """\
    Provides general information on your character including level, experience, and other attributes.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character.information(**kwargs)


@DoActions.register_subclass('inventory')
class Inventory(DoActions):
    """\
    INVENTORY allows you to view your inventory. It will list all items you have in your possession.  INVENTORY
    will not list the items within any containers you have.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.view_inventory(**kwargs)


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

        self.character.look(**kwargs)


@DoActions.register_subclass('north')
@DoActions.register_subclass('n')
class North(DoActions):
    """\
    Moves you north, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if world.tile_exists(x=self.character.location_x, y=self.character.location_y - 1, area=self.character.area):
            self.character.move_north()
        else:
            terminal_output.print_text('You cannot find a way to move in that direction.')


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

        self.character.put(**kwargs)


@DoActions.register_subclass('quit')
class Quit(DoActions):
    """\
    Exits the game.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        terminal_output.print_text("You will need to find a way to exit the game.")


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

        self.character.search(**kwargs)


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

        self.character.search(**kwargs)


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

        self.character.view_skills(**kwargs)


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

        self.character.skin(**kwargs)


@DoActions.register_subclass('south')
@DoActions.register_subclass('s')
class South(DoActions):
    """\
    Moves you south, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if world.tile_exists(x=self.character.location_x, y=self.character.location_y + 1, area=self.character.area):
            self.character.move_south()
        else:
            terminal_output.print_text("You cannot find a way to move in that direction.")


@DoActions.register_subclass('stats')
class Stats(DoActions):
    """\
    Displays your general statistics.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.character.view_stats(**kwargs)


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

        self.character.target_enemy(**kwargs)


@DoActions.register_subclass('west')
@DoActions.register_subclass('w')
class West(DoActions):
    """\
    Moves you west, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if world.tile_exists(x=self.character.location_x - 1, y=self.character.location_y, area=self.character.area):
            self.character.move_west()
        else:
            terminal_output.print_text("You cannot find a way to move in that direction.")


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

