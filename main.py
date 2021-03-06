#Insert Copywright

from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_socketio import SocketIO, send, emit
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
import shops as shops


csrf = CsrfProtect()
thread = None
lock = threading.Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dion'
app.config['DEBUG'] = True
csrf.init_app(app)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
socketio = SocketIO(app)

profession_choices = config.profession_choices
stats = config.get_stats_data_file()
available_stat_points = config.available_stat_points


class GameWindow():
    
    def __init__(self):
        self._game_window_text = []
        
    def __str__(self):
        return _game_window_text

    def print_text(self, text):
        text = text.split('\n')
        with lock:
            self._game_window_text.extend(text)
            self._game_window_text.extend(['>'])
        return
    
    def print_command(self, command):
        with lock:
            self._game_window_text[-1] = '>' + command
            self._game_window_text.extend(['>'])
        return
    

class StatusWindow():
    
    def __init__(self):
        self._status_window_text = ["Right Hand:   empty",
                                  "Left Hand:    empty",
                                  "Stance:       none",
                                  "Position:     none"]
        self._showing_status = True
        
    def __str__(self):
        return _status_window_text
    
    def print_shop_menu(self, shop_text):
        with lock:
            self._status_window_text = shop_text
            self._showing_status = False
        return
    
    def print_status(self, status):
        with lock:
            self._status_window_text = status
            self._showing_status = True
        return
    
    @property
    def status_window_text(self):
        with lock:
            return self._status_window_text
    
    @property
    def showing_status(self):
        with lock:
            return self._showing_status
    @showing_status.setter
    def showing_status(self, set_value):
        with lock:
            self._showing_status = set_value
        
global game_window    
game_window = GameWindow()
game_window.print_text("")

global status_window
status_window = StatusWindow()

player.link_game_window(game_window)
actions.link_game_window(game_window)
tiles.link_game_window(game_window)
items.link_game_window(game_window)
enemies.link_game_window(game_window)
combat.link_game_window(game_window)
npcs.link_game_window(game_window)
shops.link_game_window(game_window)
objects.link_game_window(game_window)
tiles.link_status_window(status_window)
player.link_status_window(status_window)
actions.link_status_window(status_window)
shops.link_status_window(status_window)

@app.route('/')
def index():
        return render_template('index.html', async_mode=socketio.async_mode)
    
@socketio.event
def connect():
    emit('message', {'data': 'You are connected to the server.'})
    
@socketio.event
def game_action(msg):
    emit('message', {'data': msg['data']})
    
@socketio.event
def game_event(game_event_text):
    emit('game_event_print', {'data': game_event_text})

@app.route('/new_character', methods=['POST', 'GET'])
def new_character():
    
    message = ""
        
    form = forms.NewCharacterForm()
    
    stats_initial = {}
    stats_total = 0

    if form.validate_on_submit():
        result = request.form
        first_name = result['first_name']
        last_name = result['last_name']
        gender = result['gender']
        profession = result['profession']  
        
        for stat in stats:
            stats_initial[stat.lower()] = int(result[stat])
            stats_total += stats_initial[stat.lower()]

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
        global socketio
        socketio.emit('game_event_print', {'data': character_print})
        
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
        player.character.print_status()
              
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
                player.character.room = world.tile_exists(x=player.character.location_x, y=player.character.location_y, area=player.character.area)
                player.character.room.fill_room(character=player.character)
                
        player.character.room.intro_text()
        player.character.print_status()
        
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
    

@app.route('/skills', methods=['POST', 'GET'])
def skills_modify():
    
    if not player.character:
        game_window.print_text('You do not yet have a character. Please create a new character or load a character.')
        return redirect('/')
    
    form = forms.SkillsForm()
    skill_data_file = config.get_skill_data_file()
    
    if form.validate_on_submit():
        
        result = request.form
        
        player.character.physical_training_points = result['physical_training_points_var']
        player.character.mental_training_points = result['mental_training_points_var']
        
        for skill in player.character.skills:
            player.character.skills[skill] = int(result[skill])
        
        return redirect('/')
    
    return render_template('skills.html', form=form, player=player.character, skillDataFile=skill_data_file)


if __name__ == '__main__':
    socketio.run(app)


# host='127.0.0.1', port=8080, 
