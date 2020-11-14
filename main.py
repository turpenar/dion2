#Insert Copywrite

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from wtforms import IntegerField
from datetime import datetime
import threading as threading
import pathlib as pathlib
import pickle as pickle
import abc as abc
import json as json

import config as config
import mixins as mixins
import forms as forms
import world as world
import player as player
import actions as actions
import enemies as enemies
import combat as combat
import npcs as npcs
import objects as objects
import char_gen as character_generator
import tiles as tiles
import skills as skills
import items as items


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dion'
profession_choices = config.profession_choices
stats = config.stats
available_stat_points = config.available_stat_points

lock = threading.Lock()

class GameWindow():
    
    def __init__(self):
        self.game_window_text = []
        
    def __str__(self):
        return game_window_text

    def print_text(self, text):
        text = text.split('\n')
        with lock:
            self.game_window_text.extend(text)
            self.game_window_text.extend(['>'])
        return
    
    def print_command(self, command):
        with lock:
            self.game_window_text[-1] = '>' + command
            self.game_window_text.extend(['>'])
        return
        

global game_window    
game_window = GameWindow()
game_window.print_text("")

player.link_game_window(game_window)
actions.link_game_window(game_window)
tiles.link_game_window(game_window)
items.link_game_window(game_window)
enemies.link_game_window(game_window)
combat.link_game_window(game_window)
npcs.link_game_window(game_window)

@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method == "POST":
        action_content = request.form['content']
        game_window.print_command(action_content)
        actions.do_action(action_input=action_content, character=player.character)
        return redirect('/')
        
    else:
        game_events = game_window.game_window_text
        return render_template('index.html', gameEvents=game_events)

@app.route('/new_character', methods=['POST', 'GET'])
def new_character():
    
    message = ""
        
    form = forms.NewCharacterForm()
    
    stats_initial = {}
    stats_total = 0

    if form.is_submitted():
        result = request.form
        first_name = result['first_name']
        last_name = result['last_name']
        gender = result['gender']
        profession = result['profession']  
        
        for stat in stats:
            stats_initial[stat.lower()] = int(result[stat])
            stats_total += stats_initial[stat.lower()]
        
        character_print  = '''
*** You have created a new character! ***
First Name:  {}
Last Name:  {}
Gender:  {}
Profession:  {}
            '''.format(first_name,
                       last_name,
                       gender,
                       profession)
        stat_print = ""
        for stat in stats:
            stat_print = stat_print + "\n" + stat + ":  " + str(stats_initial[stat.lower()])
        character_print = character_print + "\n" + stat_print
            
        game_window.print_text(character_print)
        
        world.load_tiles()
        player.create_character('new_player')
        
        player.character.name = first_name
        player.character.first_name = first_name
        player.character.last_name = last_name
        player.character.gender = gender
        player.character.profession = profession
        
        for stat in player.character.stats:
            player.character.stats[stat] = stats_initial[stat]
            
        player.character.set_character_attributes()    
        player.character.set_gender(player.character.gender)
        skills.level_up_skill_points()
        player.character.save()
        
        game_intro = '''
    The beast becomes restless...  hungry and tired...

                        ...it trembles with anger, and the earth shakes...

    Far away, you lay in a field surrounded by trees.    
    You close your eyes and an unsettling feeling comes over you. You dread having to go back into town and resume a 
    day you already know is going to be a waste. But you know that people rely on you and your resolve. They trust you,
    at least that's what they say. "{} really knows how to get things done," they would say.

    You open your eyes...
            '''.format(player.character.object_pronoun)
            
        game_window.print_text(game_intro)
        
        player.character.room = world.tile_exists(x=player.character.location_x, y=player.character.location_y, area=player.character.area)
        player.character.room.fill_room(character=player.character)
        player.character.room.intro_text()
              
        return redirect('/')
    return render_template('/new_character.html', form=form, Stats=stats)

@app.route('/load_character', methods=['POST', 'GET'])
def load_character():
    
    saved_characters, character_names = get_characters()

    if request.method == "POST":
        character_name = request.form['character'].split()
        
        world.load_tiles()
                
        for char_data in saved_characters:
            if char_data['_first_name'] == character_name[0] and char_data['_last_name'] == character_name[1]:
                player.create_character("new_player")
                player.character.load(state=char_data)
                
        player.character.room.intro_text()
        
        return redirect('/')
    
    
    return render_template('load_character.html', Characters=character_names)

def get_characters():
    
    saved_characters = []
    character_names = []

    path_load = pathlib.Path.cwd() / 'Profiles'
    filenames = path_load.glob('*.p')
    for filename in filenames:
        path_load_file = path_load / filename
        f = open(path_load_file.absolute().as_posix(), 'rb')
        saved_characters.append(pickle.load(f))
        
    for character in saved_characters:
        character_names.append(character['_first_name'] + " " + character['_last_name'])
    
    return saved_characters, character_names

def _get_by_name(obj_type: str, file: str, file_format=config.DATA_FORMAT) -> dict:
    with open(file) as fl:
        if file_format == "json":
            data = json.load(fl, parse_int=int, parse_float=float)
        else:
            raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
    return data

def get_skill_data_file(file=config.SKILLS_FILE, file_format=config.DATA_FORMAT) -> dict:
    with open(file) as fl:
        if file_format == "json":
            data = json.load(fl, parse_int=int, parse_float=float)
        else:
            raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
    
    return data

@app.route('/skills', methods=['POST', 'GET'])
def skills_modify():
    
    skill_data_file = get_skill_data_file()
    skill_categories = list(skill_data_file.keys())
    all_skills = {}
    for category in skill_categories:
        all_skills[category] = [x.replace("_", " ").title() for x in list(skill_data_file[category].keys())]

    
    if request.method == "POST":
        return redirect('/')
    
    return render_template('skills.html', skillCategories=skill_categories, skills=all_skills, skillDataFile=skill_data_file)



if __name__ == '__main__':
    app.run(debug=True)


# host='127.0.0.1', port=8080, 
