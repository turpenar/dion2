from flask import session, redirect, url_for, render_template, request, flash
from datetime import datetime
import threading as threading
import pathlib as pathlib
import pickle as pickle
import abc as abc
import json as json
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from app import socketio, login_manager, db
from app.main import datadef, main, events, world, player, skills, config, items
from app.main.forms import LoginForm, SignUpForm, NewCharacterForm, SkillsForm

@login_manager.user_loader
def load_user(user_id):
    return datadef.User.query.get(int(user_id))

@main.route('/')
@login_required
def index():
    return render_template('/index.html', async_mode=socketio.async_mode)

@main.route('/login', methods=['POST', 'GET'])
def login():
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = datadef.User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.index'))

        return '<h1>Invalid username or password</h1>'
    return render_template('/login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = datadef.User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return '<h1>New user has been created!</h1>'
    
    return render_template('/signup.html', form=form)
    
@main.route('/new_character', methods=['POST', 'GET'])
@login_required
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
        
        current_user.character_1 = player.character
        db.session.commit()

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
        player.character.get_status()
        
        landing_page_text = "Character Created! Please close the window and return to the game window."
              
        return render_template('/close.html', text=landing_page_text)
        
    return render_template('/new_character.html', form=form, Stats=stats)

@main.route('/load_character', methods=['POST', 'GET'])
@login_required
def load_character():
    
    characters = []
    character_names = []
    
    if current_user.character_1:
        characters.append(current_user.character_1)
    if current_user.character_2:
        characters.append(current_user.character_2)
    if current_user.character_3:
        characters.append(current_user.character_3)            
    if current_user.character_4:
        characters.append(current_user.character_4)    
    if current_user.character_5:
        characters.append(current_user.character_5) 
        
    for character in characters:
           character_names.append(character.first_name)

    if request.method == "POST":
        character_name = request.form['character']
        
        world.load_tiles()
                
        for character in characters:
            if character.first_name == character_name:
                player.character = character
                player.character.room = world.tile_exists(x=player.character.location_x, y=player.character.location_y, area=player.character.area)
                player.character.room.fill_room(character=player.character)
                
        player.character.room.intro_text()
        player.character.get_status()
        
        landing_page_text = "Character Loaded! Please close the window and return to the game window."
        
        return render_template('/close.html', text=landing_page_text)
    
    return render_template('/load_character.html', Characters=character_names)
    

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
