

"""

TODO: A player can continue opening the skills screen and incrementing skill. Should stop at 2 per level.


"""

import tkinter as tk
import copy as copy

import player as player
import config as config


global terminal_output
profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.base_training_points


def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal


def level_up_skill_points():

    stat_value = {}

    for stat in player.character.stats:
        stat_value[stat] = int(round(float(player.character.get_stat(stat)))) * int(profession_skillpoint_bonus_file.loc[player.character.get_profession(), stat])

    added_physical_points = base_training_points + ((stat_value['strength']
                                                    + stat_value['constitution']
                                                    + stat_value['dexterity']
                                                    + stat_value['agility']) / 20)
    added_mental_points = base_training_points + ((stat_value['intellect']
                                                   + stat_value['wisdom']
                                                   + stat_value['logic']
                                                   + stat_value['spirit']) / 20)

    player.character.set_physical_training_points(player.character.get_physical_training_points() + added_physical_points)
    player.character.set_mental_training_points(player.character.get_mental_training_points() + added_mental_points)

    for skill in player.character.skills:
        player.character.set_skill_base(skill=skill, value=player.character.get_skill(skill))


class TrainingPoints(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.physical_points_var = tk.IntVar()
        self.physical_points_var.set(player.character.get_physical_training_points())
        self.physical_points_label = tk.Label(self, text="Physical Training Points = ")
        self.physical_points_label.grid(row=0, column=0)
        self.physical_points = tk.Label(self, textvariable=self.physical_points_var)
        self.physical_points.grid(row=0, column=1)

        self.mental_points_var = tk.IntVar()
        self.mental_points_var.set(player.character.get_mental_training_points())
        self.mental_points_label = tk.Label(self, text="Mental Training Points = ")
        self.mental_points_label.grid(row=0, column=2)
        self.mental_points = tk.Label(self, textvariable=self.mental_points_var)
        self.mental_points.grid(row=0, column=3)


class WeaponSkills(tk.Frame):
    def __init__(self, parent, training_points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.training_points = training_points
        self.all_skills = {}

        self.weapon_skills_label = tk.Label(self, text="Weapons Skills")
        self.weapon_skills_label.grid(row=0, column=0)

        self.skill_names = ['edged_weapons', 'blunt_weapons', 'polearm_weapons']
        self.skill_labels = ['Edged Weapons', 'Blunt Weapons', 'Polearm Weapons']
        self.skills = {}
        row = 1

        for skill_name, skill_label in zip(self.skill_names, self.skill_labels):

            self.skills[skill_name] = {}

            self.skills[skill_name]['skill_var_start'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var_start'].set(player.character.get_skill_base(skill_name))

            self.skills[skill_name]['skill_var'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var'].set(player.character.get_skill(skill_name))
            self.all_skills[skill_name] = self.skills[skill_name]['skill_var']

            self.skills[skill_name]['skill_label'] = tk.Label(self, text=skill_label)
            self.skills[skill_name]['skill_label'].grid(row=row, column=0)

            self.skills[skill_name]['skill_decrease'] = tk.Button(self, text="-", command=lambda x=self.skills[skill_name]['skill_var']: self.decrease_skill(x))
            self.skills[skill_name]['skill_decrease'].grid(row=row, column=1)

            self.skills[skill_name]['skill_value'] = tk.Label(self, textvariable=self.skills[skill_name]['skill_var'])
            self.skills[skill_name]['skill_value'].grid(row=row, column=2)

            self.skills[skill_name]['skill_increase'] = tk.Button(self, text="+",
                                                   command=lambda x=self.skills[skill_name]['skill_var'],
                                                                  y=self.skills[skill_name]['skill_var_start']: self.increase_skill(x,y))
            self.skills[skill_name]['skill_increase'].grid(row=row, column=3)

            row += 1

    def increase_skill(self, skill_var, skill_var_start):
        if skill_var.get() >= skill_var_start.get() + 2:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() - 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() - 1)
        skill_var.set(skill_var.get() + 1)

    def decrease_skill(self, skill_var):
        if skill_var.get() == 0:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() + 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() + 1)
        skill_var.set(skill_var.get() - 1)

    def calculate_increment(self):
        pass


class ArmorSkills(tk.Frame):
    def __init__(self, parent, training_points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.training_points = training_points
        self.all_skills = {}

        self.armor_skills_label = tk.Label(self, text="Armor Skills")
        self.armor_skills_label.grid(row=0, column=0)

        self.skill_names = ['armor', 'shield']
        self.skill_labels = ['Armor', 'Shield']
        self.skills = {}
        row = 1

        for skill_name, skill_label in zip(self.skill_names, self.skill_labels):

            self.skills[skill_name] = {}

            self.skills[skill_name]['skill_var_start'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var_start'].set(player.character.get_skill_base(skill_name))

            self.skills[skill_name]['skill_var'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var'].set(player.character.get_skill(skill_name))
            self.all_skills[skill_name] = self.skills[skill_name]['skill_var']

            self.skills[skill_name]['skill_label'] = tk.Label(self, text=skill_label)
            self.skills[skill_name]['skill_label'].grid(row=row, column=0)

            self.skills[skill_name]['skill_decrease'] = tk.Button(self, text="-", command=lambda x=self.skills[skill_name]['skill_var']: self.decrease_skill(x))
            self.skills[skill_name]['skill_decrease'].grid(row=row, column=1)

            self.skills[skill_name]['skill_value'] = tk.Label(self, textvariable=self.skills[skill_name]['skill_var'])
            self.skills[skill_name]['skill_value'].grid(row=row, column=2)

            self.skills[skill_name]['skill_increase'] = tk.Button(self, text="+",
                                                   command=lambda x=self.skills[skill_name]['skill_var'],
                                                                  y=self.skills[skill_name]['skill_var_start']: self.increase_skill(x,y))
            self.skills[skill_name]['skill_increase'].grid(row=row, column=3)

            row += 1

    def increase_skill(self, skill_var, skill_var_start):
        if skill_var.get() >= skill_var_start.get() + 2:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() - 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() - 1)
        skill_var.set(skill_var.get() + 1)

    def decrease_skill(self, skill_var):
        if skill_var.get() == 0:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() + 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() + 1)
        skill_var.set(skill_var.get() - 1)


class CombatSkills(tk.Frame):
    def __init__(self, parent, training_points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.training_points = training_points
        self.all_skills = {}

        self.combat_skills_label = tk.Label(self, text="Combat Skills")
        self.combat_skills_label.grid(row=0, column=0)

        self.skill_names = ['dodging']
        self.skill_labels = ['Dodging']
        self.skills = {}
        row = 1

        for skill_name, skill_label in zip(self.skill_names, self.skill_labels):

            self.skills[skill_name] = {}

            self.skills[skill_name]['skill_var_start'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var_start'].set(player.character.get_skill_base(skill_name))

            self.skills[skill_name]['skill_var'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var'].set(player.character.get_skill(skill_name))
            self.all_skills[skill_name] = self.skills[skill_name]['skill_var']

            self.skills[skill_name]['skill_label'] = tk.Label(self, text=skill_label)
            self.skills[skill_name]['skill_label'].grid(row=row, column=0)

            self.skills[skill_name]['skill_decrease'] = tk.Button(self, text="-", command=lambda x=self.skills[skill_name]['skill_var']: self.decrease_skill(x))
            self.skills[skill_name]['skill_decrease'].grid(row=row, column=1)

            self.skills[skill_name]['skill_value'] = tk.Label(self, textvariable=self.skills[skill_name]['skill_var'])
            self.skills[skill_name]['skill_value'].grid(row=row, column=2)

            self.skills[skill_name]['skill_increase'] = tk.Button(self, text="+",
                                                   command=lambda x=self.skills[skill_name]['skill_var'],
                                                                  y=self.skills[skill_name]['skill_var_start']: self.increase_skill(x,y))
            self.skills[skill_name]['skill_increase'].grid(row=row, column=3)

            row += 1

    def increase_skill(self, skill_var, skill_var_start):
        if skill_var.get() >= skill_var_start.get() + 2:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() - 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() - 1)
        skill_var.set(skill_var.get() + 1)

    def decrease_skill(self, skill_var):
        if skill_var.get() == 0:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() + 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() + 1)
        skill_var.set(skill_var.get() - 1)


class SurvivalSkills(tk.Frame):
    def __init__(self, parent, training_points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.training_points = training_points
        self.all_skills = {}

        self.survival_skills_label = tk.Label(self, text="Survival Skills")
        self.survival_skills_label.grid(row=0, column=0)

        self.skill_names = ['physical_fitness', 'perception']
        self.skill_labels = ['Physical Fitness', 'Perception']
        self.skills = {}
        row = 1

        for skill_name, skill_label in zip(self.skill_names, self.skill_labels):

            self.skills[skill_name] = {}

            self.skills[skill_name]['skill_var_start'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var_start'].set(player.character.get_skill_base(skill_name))

            self.skills[skill_name]['skill_var'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var'].set(player.character.get_skill(skill_name))
            self.all_skills[skill_name] = self.skills[skill_name]['skill_var']

            self.skills[skill_name]['skill_label'] = tk.Label(self, text=skill_label)
            self.skills[skill_name]['skill_label'].grid(row=row, column=0)

            self.skills[skill_name]['skill_decrease'] = tk.Button(self, text="-", command=lambda x=self.skills[skill_name]['skill_var']: self.decrease_skill(x))
            self.skills[skill_name]['skill_decrease'].grid(row=row, column=1)

            self.skills[skill_name]['skill_value'] = tk.Label(self, textvariable=self.skills[skill_name]['skill_var'])
            self.skills[skill_name]['skill_value'].grid(row=row, column=2)

            self.skills[skill_name]['skill_increase'] = tk.Button(self, text="+",
                                                   command=lambda x=self.skills[skill_name]['skill_var'],
                                                                  y=self.skills[skill_name]['skill_var_start']: self.increase_skill(x,y))
            self.skills[skill_name]['skill_increase'].grid(row=row, column=3)

            row += 1

    def increase_skill(self, skill_var, skill_var_start):
        if skill_var.get() >= skill_var_start.get() + 2:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() - 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() - 1)
        skill_var.set(skill_var.get() + 1)

    def decrease_skill(self, skill_var):
        if skill_var.get() == 0:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() + 2)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() + 1)
        skill_var.set(skill_var.get() - 1)


class Skills:
    def __init__(self, parent):

        self.parent = parent
        self.frame = tk.Frame(self.parent, width=100)

        self.training_points = TrainingPoints(self.parent)
        self.training_points.grid(row=0, column=0)

        self.weapons_skills = WeaponSkills(self.parent, self.training_points)
        self.weapons_skills.grid(row=1, column=0)

        self.armor_skills = ArmorSkills(self.parent, self.training_points)
        self.armor_skills.grid(row=2, column=0)

        self.combat_skills = CombatSkills(self.parent, self.training_points)
        self.combat_skills.grid(row=3, column=0)

        self.survival_skills = SurvivalSkills(self.parent, self.training_points)
        self.survival_skills.grid(row=4, column=0)

        self.label = tk.Label(self.frame)
        self.label.grid(row=5, column=0)
        self.button1 = tk.Button(self.frame, text="Update Skills", command=self.update_skills)
        self.button1.grid(row=6, column=0)
        self.frame.grid()

        self.all_skills = {}

        for d in (self.weapons_skills.all_skills, self.armor_skills.all_skills, self.combat_skills.all_skills, self.survival_skills.all_skills):
            self.all_skills.update(d)

    def update_skills(self):

        for skill in self.all_skills:
            player.character.set_skill(skill, int(self.all_skills[skill].get()))
            
        for skill in self.all_skills:
            skill_value = int(self.all_skills[skill].get())
            if skill_value <= 10:
                player.character.set_skill_bonus(skill=skill, value=int(skill_value * 5))
            elif skill_value <= 20:
                player.character.set_skill_bonus(skill=skill, value=(50 + int((skill_value - 10) * 4)))
            elif skill_value <= 30:
                player.character.set_skill_bonus(skill=skill, value=(90 + int((skill_value - 20) * 3)))
            elif skill_value <= 40:
                player.character.set_skill_bonus(skill=skill, value=(120 + int((skill_value - 30) * 2)))
            elif skill_value <= 50:
                player.character.set_skill_bonus(skill=skill, value=(140 + int((skill_value - 40) * 1)))

        self.close_window()

    def close_window(self):
        self.parent.destroy()

