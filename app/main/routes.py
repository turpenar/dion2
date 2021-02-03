from flask import session, redirect, url_for, render_template, request
from datetime import datetime
import threading as threading
import pathlib as pathlib
import pickle as pickle
import abc as abc
import json as json

from app import socketio
from app.main import main, events, world, player, skills, config, items
from app.main.forms import NewCharacterForm, SkillsForm


@main.route('/')
def index():
    return render_template('/index.html', async_mode=socketio.async_mode)
    
@main.route('/new_character', methods=['POST', 'GET'])
def new_character():
    
    message = ""
        
    form = NewCharacterForm()
    
    stats = config.get_stats_data_file()
    
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

        events.game_event(character_print)
        
        game_intro = '''
    The beast becomes restless...  hungry and tired...

                        ...it trembles with anger, and the earth shakes...

    Far away, you lay in a field surrounded by trees.    
    You close your eyes and an unsettling feeling comes over you. You dread having to go back into town and resume a 
    day you already know is going to be a waste. But you know that people rely on you and your resolve. They trust you,
    at least that's what they say. "{} really knows how to get things done," they would say.

    You open your eyes...
            '''.format(player.character.object_pronoun)
            
        events.game_event(game_intro)
        
        player.character.room = world.tile_exists(x=player.character.location_x, y=player.character.location_y, area=player.character.area)
        player.character.room.fill_room(character=player.character)
        player.character.room.intro_text()
        player.character.print_status()
        
        landing_page_text = "Character Created! Please close the window and return to the game window."
              
        return render_template('/close.html', text=landing_page_text)
        
    return render_template('/new_character.html', form=form, Stats=stats)

@main.route('/load_character', methods=['POST', 'GET'])
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
        
        landing_page_text = "Character Loaded! Please close the window and return to the game window."
        
        return render_template('/close.html', text=landing_page_text)
    
    return render_template('/load_character.html', Characters=character_names)

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
    

@main.route('/skills', methods=['POST', 'GET'])
def skills_modify():
    
    if not player.character:
        landing_page_text = "You do not yet have a character. Please create a new character or load a character."
        return render_template('/close.html', text=landing_page_text)
    
    form = SkillsForm()
    skill_data_file = config.get_skill_data_file()
    
    if form.validate_on_submit():
        
        result = request.form
        
        player.character.physical_training_points = result['physical_training_points_var']
        player.character.mental_training_points = result['mental_training_points_var']
        
        for skill in player.character.skills:
            player.character.skills[skill] = int(result[skill])
            
        landing_page_text = "Skills updated! Please close the window and return to the game window."
        
        return render_template('/close.html', text=landing_page_text)
    
    return render_template('/skills.html', form=form, player=player.character, skillDataFile=skill_data_file)
