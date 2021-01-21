

"""

"""

import tkinter as tk
import copy as copy

import player as player
import config as config
import mixins as mixins


global terminal_output
profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.base_training_points


def link_terminal(terminal):
    global terminal_output
    terminal_output = terminal


def level_up_skill_points():

    stat_value = {}

    for stat in player.character.stats:
        stat_value[stat] = int(round(float(player.character.stats[stat]))) * int(profession_skillpoint_bonus_file.loc[player.character.profession, stat])

    added_physical_points = base_training_points + ((stat_value['strength']
                                                    + stat_value['constitution']
                                                    + stat_value['dexterity']
                                                    + stat_value['agility']) / 20)
    added_mental_points = base_training_points + ((stat_value['intellect']
                                                   + stat_value['wisdom']
                                                   + stat_value['logic']
                                                   + stat_value['spirit']) / 20)

    player.character.physical_training_points = player.character.physical_training_points + added_physical_points
    player.character.mental_training_points = player.character.mental_training_points + added_mental_points

    for skill in player.character.skills:
        player.character.skills_base[skill] = player.character.skills[skill]


class TrainingPoints(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.physical_points_var = tk.IntVar()
        self.physical_points_var.set(player.character.physical_training_points)
        self.physical_points_label = tk.Label(self, text="Physical Training Points = ")
        self.physical_points_label.grid(row=0, column=0)
        self.physical_points = tk.Label(self, textvariable=self.physical_points_var)
        self.physical_points.grid(row=0, column=1)

        self.mental_points_var = tk.IntVar()
        self.mental_points_var.set(player.character.mental_training_points)
        self.mental_points_label = tk.Label(self, text="Mental Training Points = ")
        self.mental_points_label.grid(row=0, column=2)
        self.mental_points = tk.Label(self, textvariable=self.mental_points_var)
        self.mental_points.grid(row=0, column=3)


class SkillDetails(tk.Frame, mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, parent, skill_category, training_points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.training_points = training_points
        self.skill_category_file = self.get_skill_category_by_name(name=skill_category)
        self.all_skills = {}
        
        self.weapon_skills_label = tk.Label(self, text=skill_category + " Skills")
        self.weapon_skills_label.grid(row=0, column=0)
        
        self.physical_points_label = tk.Label(self, text="PT")
        self.physical_points_label.grid(row=0, column=4)
        
        self.mental_points_label = tk.Label(self, text="MT")
        self.mental_points_label.grid(row=0, column=5)

        self.skills = {}
         
        row = 1
 
        for skill_name in self.skill_category_file:
 
            self.skills[skill_name] = {}
 
            self.skills[skill_name]['skill_var_start'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var_start'].set(player.character.skills_base[skill_name])
 
            self.skills[skill_name]['skill_var'] = tk.IntVar(self)
            self.skills[skill_name]['skill_var'].set(player.character.skills[skill_name])
            self.all_skills[skill_name] = self.skills[skill_name]['skill_var']
 
            self.skills[skill_name]['skill_label'] = tk.Label(self, text=skill_name.replace("_", " ").title())
            self.skills[skill_name]['skill_label'].grid(row=row, column=0)
 
            self.skills[skill_name]['skill_decrease'] = tk.Button(self, text="-", command=lambda x=self.skills[skill_name]['skill_var'],
                                                                                                 y=self.skill_category_file[skill_name]['physical_points'],
                                                                                                 z=self.skill_category_file[skill_name]['mental_points']: self.decrease_skill(x,y,z))
            self.skills[skill_name]['skill_decrease'].grid(row=row, column=1)
 
            self.skills[skill_name]['skill_value'] = tk.Label(self, textvariable=self.skills[skill_name]['skill_var'])
            self.skills[skill_name]['skill_value'].grid(row=row, column=2)
 
            self.skills[skill_name]['skill_increase'] = tk.Button(self, text="+",
                                                   command=lambda x=self.skills[skill_name]['skill_var'],
                                                                  y=self.skills[skill_name]['skill_var_start'],
                                                                  z=self.skill_category_file[skill_name]['physical_points'],
                                                                  l=self.skill_category_file[skill_name]['mental_points']: self.increase_skill(x,y,z,l))
            self.skills[skill_name]['skill_increase'].grid(row=row, column=3)
            
            self.skills[skill_name]['physical_points'] = tk.Label(self, text=self.skill_category_file[skill_name]['physical_points'])
            self.skills[skill_name]['physical_points'].grid(row=row, column=4)
            
            self.skills[skill_name]['mental_points'] = tk.Label(self, text=self.skill_category_file[skill_name]['mental_points'])
            self.skills[skill_name]['mental_points'].grid(row=row, column=5)   
 
            row += 1

    def increase_skill(self, skill_var, skill_var_start, physical_points, mental_points):
        if skill_var.get() >= skill_var_start.get() + 2:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() - physical_points)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() - mental_points)
        skill_var.set(skill_var.get() + 1)

    def decrease_skill(self, skill_var, physical_points, mental_points):
        if skill_var.get() == 0:
            return

        self.training_points.physical_points_var.set(self.training_points.physical_points_var.get() + physical_points)
        self.training_points.mental_points_var.set(self.training_points.mental_points_var.get() + mental_points)
        skill_var.set(skill_var.get() - 1)

    def calculate_increment(self):
        pass


class Skills:
    def __init__(self, parent):

        self.parent = parent
        self.frame = tk.Frame(self.parent, width=100)

        self.training_points = TrainingPoints(self.parent)
        self.training_points.grid(row=0, column=0)

        self.weapons_skills = SkillDetails(self.parent, 'Weapons', self.training_points)
        self.weapons_skills.grid(row=1, column=0)

        self.armor_skills = SkillDetails(self.parent, 'Armor', self.training_points)
        self.armor_skills.grid(row=2, column=0)

        self.combat_skills = SkillDetails(self.parent, 'Combat', self.training_points)
        self.combat_skills.grid(row=3, column=0)

        self.survival_skills = SkillDetails(self.parent, 'Survival', self.training_points)
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
            player.character.skills[skill] = int(self.all_skills[skill].get())
            
        for skill in self.all_skills:
            skill_value = int(self.all_skills[skill].get())
            if skill_value <= 10:
                player.character.skills_bonus[skill] = int(skill_value * 5)
            elif skill_value <= 20:
                player.character.skills_bonus[skill] = (50 + int((skill_value - 10) * 4))
            elif skill_value <= 30:
                player.character.skills_bonus[skill] = (90 + int((skill_value - 20) * 3))
            elif skill_value <= 40:
                player.character.skills_bonus[skill] = (120 + int((skill_value - 30) * 2))
            elif skill_value <= 50:
                player.character.skills_bonus[skill] = (140 + int((skill_value - 40) * 1))

        self.close_window()

    def close_window(self):
        self.parent.destroy()

