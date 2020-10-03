#Insert Copywrite

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading as threading
import pathlib as pathlib
import pickle as pickle

import config as config
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

import scratch as scratch


app = Flask(__name__)
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

scratch.link_game_window(game_window)
player.link_game_window(game_window)

@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method == "POST":
        event_content = request.form['content']
        game_window.print_command(event_content)
        return redirect('/')
        
    else:
        game_events = game_window.game_window_text
        return render_template('index.html', gameEvents=game_events)

@app.route('/new_character', methods=['POST', 'GET'])
def new_character():
    
    message = ""
    
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        profession = request.form['profession']
        
        stats_initial = {}
        stats_total = 0
        
        for stat in stats:
            stats_initial[stat.lower()] = int(request.form[stat])
            stats_total += stats_initial[stat.lower()]
            
        if stats_total > available_stat_points:
            message = "You have exceeded the allowed stat points."
        if stats_total <= available_stat_points:
            
            world.load_tiles()
            player.create_character('new_player')
            
            player.character.name = first_name
            player.character.first_name = first_name
            player.character.last_name = last_name
            player.character.gender = gender
            player.character.profession = profession
            
            for stat in player.character.stats:
                player.character.stats[stat] = stats_initial[stat]
                
            player.character.set_gender(player.character.gender)
            skills.level_up_skill_points()
            player.character.set_character_attributes()
            
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
            return redirect('/')
        
    return render_template('new_character.html', ProfessionChoices=profession_choices, Stats=stats, AvailableStatPoints=available_stat_points, outputMessage=message)

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
def skills():
    
    if request.method == "POST":
        return redirect('/')
    
    return render_template('skills.html')



if __name__ == '__main__':
    app.run(debug=True)


# host='127.0.0.1', port=8080, 
