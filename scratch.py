"""
This module is the main gateway to the game. It contains start menu text and basic character setup.
"""

import pathlib as pathlib
import pickle as pickle
import time as time

import player as player
import world as world


def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal


def new_character_introduction(character):
    print('''\n
The beast becomes restless...  hungry and tired...
    \
    ''')
    time.sleep(5)
    print('''\
                    ...it trembles with anger, and the earth shakes...
    \
    ''')
    time.sleep(5)
    print('''\

Far away, you lay in a field surrounded by trees.    
You close your eyes and an unsettling feeling comes over you. You dread having to go back into town and resume a 
day you already know is going to be a waste. But you know that people rely on you and your resolve. They trust you,
at least that's what they say. "That {}, {} really knows how to get things done."

You open your eyes...
    \
    '''.format(character.name, character.object_pronoun))
    time.sleep(10)


def splash_screen():
    welcome_screen = """\
    ################################################################
    ####                    Welcome to Dion                     ####
    ################################################################

                            [1] New Character
                            [2] Load Character
    \
    """

    terminal_output.print_text(welcome_screen)


def play():
    path_load = pathlib.Path.cwd() / 'Profiles'
    filenames = path_load.glob('*.p')
    saved_characters = []
    for filename in filenames:
        path_load_file = path_load / filename
        f = open(path_load_file.absolute().as_posix(), 'rb')
        saved_characters.append(pickle.load(f))

    saved_character_names = []

    for character in saved_characters:
        saved_character_names.append(character['first_name'])

    saved_character_names_print = ""
    if len(saved_character_names) == 0:
        saved_character_names_print = "None"
    else:
        for name in saved_character_names:
            saved_character_names_print = saved_character_names_print + "[" + name + "]" + "\n\t"

    character = None
    char_found = False
    while char_found == False:
        option = input('> ')

        if option == 'New':
            character = player.Player(player_name='new_player')
            char_found = True

            first_name = input("Please provide a first name for your character:  ")
            last_name = input("Please provide a last name for your character:  ")
            gender_options = ["male", "female"]

            while character.gender == "None":
                gender = input("What is your character's gender [male/female]:  ")
                if gender == "male" or gender == "female":
                    character.set_gender(gender)
                else:
                    print("That is an invalid input")
                    print("Please choose {}".format(gender_options))

            character.name = first_name
            character.first_name = first_name
            character.last_name = last_name

            new_character_introduction(character)

        elif set(saved_character_names) & {option}:
            for char_data in saved_characters:
                if char_data['first_name'] == option:
                    character = player.Player(player_name='new_player')
                    character.load(state=char_data)
                    char_found = True
        else:
            print("That is not an option. Please select from the available options.")

    terminal_output.print_text("""\

    ***  Type HELP for a list of commands available to you. Type HELP <command> for assistance with a particular
    command usage.  ***
    \
    """)


