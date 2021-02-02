from flask import session, redirect, url_for, render_template, request

from app import socketio
from app.main import main, events, world, player, skills, config
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
              
        return render_template('/close.html')
        
    return render_template('/new_character.html', form=form, Stats=stats)