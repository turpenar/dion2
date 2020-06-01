
import tkinter as tk
import pathlib as pathlib
import pickle as pickle
import math as math

import player as player
import world as world
import config as config
import skills as skills

global terminal_output

def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal

class General(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.first_name_label = tk.Label(self, text="First Name")
        self.first_name_label.grid(row=0, column=0)

        self.first_name_entry = tk.Entry(self, width=25)
        self.first_name_entry.grid(row=1, column=0)

        self.last_name_label = tk.Label(self, text="Last Name")
        self.last_name_label.grid(row=2, column=0)

        self.last_name_entry = tk.Entry(self, width=25)
        self.last_name_entry.grid(row=3, column=0)

        self.gender_label = tk.Label(self, text="Gender")
        self.gender_label.grid(row=4, column=0)

        self.genderVar = tk.StringVar(self.parent)
        gender_choices = config.gender_choices
        self.genderVar.set('None')

        self.gender_entry = tk.OptionMenu(self, self.genderVar, *gender_choices)
        self.gender_entry.grid(row=5, column=0)


class Profession(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.profession_label = tk.Label(self, text="Profession")
        self.profession_label.grid(row=0, column=0)

        self.professionVar = tk.StringVar(self.parent)
        profession_choices = config.profession_choices
        self.professionVar.set('None')

        self.profession_entry = tk.OptionMenu(self, self.professionVar, *profession_choices)
        self.profession_entry.grid(row=1, column=0)


class Stats(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.all_entries = {}

        self.remainingVar = tk.IntVar()
        self.remainingVar.set(528)
        self.remaining_points_label = tk.Label(self, text="Remaining Points = ")
        self.remaining_points_label.grid(row=0, column=0)
        self.remaining_points = tk.Label(self, textvariable=self.remainingVar)
        self.remaining_points.grid(row=0, column=1)

        self.strength_label = tk.Label(self, text="Strength")
        self.strength_label.grid(row=1, column=0)

        validatecommand = (self.register(self.check_entry), '%d', '%i', '%P', '%s', '%S')

        self.strength_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.strength_entry.grid(row=1, column=1)
        self.all_entries['strength'] = self.strength_entry

        self.constitution_label = tk.Label(self, text="Constitution")
        self.constitution_label.grid(row=2, column=0)

        self.constitution_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.constitution_entry.grid(row=2, column=1)
        self.all_entries['constitution'] = self.constitution_entry

        self.dexterity_label = tk.Label(self, text="Dexterity")
        self.dexterity_label.grid(row=3, column=0)

        self.dexterity_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.dexterity_entry.grid(row=3, column=1)
        self.all_entries['dexterity'] = self.dexterity_entry

        self.agility_label = tk.Label(self, text="Agility")
        self.agility_label.grid(row=4, column=0)

        self.agility_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.agility_entry.grid(row=4, column=1)
        self.all_entries['agility'] = self.agility_entry

        self.intellect_label = tk.Label(self, text="Intellect")
        self.intellect_label.grid(row=1, column=3)

        self.intellect_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.intellect_entry.grid(row=1, column=4)
        self.all_entries['intellect'] = self.intellect_entry

        self.wisdom_label = tk.Label(self, text="Wisdom")
        self.wisdom_label.grid(row=2, column=3)

        self.wisdom_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.wisdom_entry.grid(row=2, column=4)
        self.all_entries['wisdom'] = self.wisdom_entry

        self.logic_label = tk.Label(self, text="Logic")
        self.logic_label.grid(row=3, column=3)

        self.logic_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.logic_entry.grid(row=3, column=4)
        self.all_entries['logic'] = self.logic_entry

        self.spirit_label = tk.Label(self, text="Spirit")
        self.spirit_label.grid(row=4, column=3)

        self.spirit_entry = tk.Entry(self, width=8, validate='key', validatecommand=validatecommand)
        self.spirit_entry.grid(row=4, column=4)
        self.all_entries['spirit'] = self.spirit_entry

    def check_entry(self, action_type, index, value_post, value_prior, addition):

        if value_prior == '':
            value_prior = 0
        if value_post == '':
            val_post = 0
            val_prior = int(value_prior)
            val_change = val_post - val_prior
            self.reset_remaining(val_change)
            return True

        if not value_post.isdigit():
            return False
        val_post = int(value_post)
        val_prior = int(value_prior)

        if (val_post < 0) + (val_post > 100):
            return False
        val_change = val_post - val_prior
        if val_change > self.remainingVar.get():
            return False

        self.reset_remaining(val_change)

        return True

    def reset_remaining(self, change):
        old_remaining = self.remainingVar.get()
        new_remaining = old_remaining - change
        self.remainingVar.set(new_remaining)
        self.master.update_idletasks()


class CharacterGenerator:
    def __init__(self, parent, character_created_var):

        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.character_created_var = character_created_var
        self.stats = {}

        self.general = General(self.parent)
        self.general.grid(row=0, column=0)

        self.profession = Profession(self.parent)
        self.profession.grid(row=1, column=0)

        self.stats = Stats(self.parent)
        self.stats.grid(row=3, column=0)

        self.label = tk.Label(self.frame)
        self.label.grid(row=4, column=0)
        self.button1 = tk.Button(self.frame, text="Create Character", command=self.create_character)
        self.button1.grid(row=5, column=0)
        self.frame.grid()

    def create_character(self):

        total_stats = 0
        available_stat_points = config.available_stat_points
        base_training_points = config.base_training_points

        if self.general.first_name_entry.get() == '':
            self.popupmsg("Please create a first name.")
            return

        if self.general.last_name_entry.get() == '':
            self.popupmsg("Please create a last name.")
            return

        if self.general.genderVar.get() == 'None':
            self.popupmsg("You need to select a gender.")
            return

        if self.profession.professionVar.get() == 'None':
            self.popupmsg("You need to select a profession.")
            return

        for entry in self.stats.all_entries:
            if not self.stats.all_entries[entry].get():
                self.popupmsg(entry + " has no value!")
                return

            total_stats += int(self.stats.all_entries[entry].get())

        if total_stats != available_stat_points:
            self.popupmsg("Your stats total does not equal " + str(available_stat_points) + ".")
            return

        world.load_tiles()
        player.create_character('new_player')

        player.character.name = self.general.first_name_entry.get()
        player.character.first_name = self.general.first_name_entry.get()
        player.character.last_name = self.general.last_name_entry.get()
        player.character.gender = self.general.genderVar.get()

        player.character.profession = self.profession.professionVar.get()

        for stat in player.character.stats:
            player.character.stats[stat] = int(self.stats.all_entries[stat].get())
        
        player.character.set_gender(player.character.gender)
        skills.level_up_skill_points()
        player.character.set_character_attributes()

        player.character.save()

        terminal_output.print_text('''
You have created {} {}

<Press Enter>
                                    \
                                    '''.format(player.character.first_name,
                                               player.character.last_name))

        self.character_created_var.set(True)
        self.close_window()

    def popupmsg(self, msg):
        self.popup = tk.Tk()
        self.popup.wm_title("Whoops!")
        label = tk.Label(self.popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tk.Button(self.popup, text="Okay", command=self.popup.destroy)
        B1.pack()
        self.popup.mainloop()

    def close_window(self):
        self.parent.destroy()


class CharacterLoader:
    def __init__(self, parent, character_created_var):

        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.character_created_var = character_created_var
        self.saved_characters = []

        self.gender_label = tk.Label(self.frame, text="Select a character")
        self.gender_label.grid(row=1, column=0)

        self.charVar = tk.StringVar(self.frame)
        self.char_choices = self.get_characters()
        self.charVar.set("Choose Character")

        self.gender_entry = tk.OptionMenu(self.frame, self.charVar, *self.char_choices)
        self.gender_entry.grid(row=2, column=0)

        self.label = tk.Label(self.frame)
        self.label.grid(row=3, column=0)
        self.button1 = tk.Button(self.frame, text="Load Character", command=self.load_character)
        self.button1.grid(row=4, column=0)
        self.frame.grid()

    def load_character(self):

        char_name = self.charVar.get()

        world.load_tiles()

        for char_data in self.saved_characters:
            if char_data['_first_name'] == char_name:
                player.create_character("new_player")
                player.character.load(state=char_data)

        terminal_output.print_text('''
You have loaded {} {}

***  Type HELP for a list of commands available to you. Type HELP <command> for assistance with a particular
command usage.  ***

<Press Enter>
                                    \
                                    '''.format(player.character.first_name,
                                               player.character.last_name))

        self.character_created_var.set(True)
        self.close_window()

    def get_characters(self):

        path_load = pathlib.Path.cwd() / 'Profiles'
        filenames = path_load.glob('*.p')
        for filename in filenames:
            path_load_file = path_load / filename
            f = open(path_load_file.absolute().as_posix(), 'rb')
            self.saved_characters.append(pickle.load(f))

        saved_character_names = []

        for character in self.saved_characters:
            saved_character_names.append(character['_first_name'])

        return saved_character_names

    def close_window(self):
        self.parent.destroy()