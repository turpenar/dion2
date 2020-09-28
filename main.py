#Insert Copywrite

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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


app = Flask(__name__)

game_window_text = list()
profession_choices = config.profession_choices
stats = config.stats

def print_text(text):
    game_window_text.append(text)
    return

@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method == "POST":
        event_content = request.form['content']
        
        try:
            print_text(event_content)
            
            
            
            return redirect('/')
        except:
            return "There was an issue adding your item"
        
    else:
        events = game_window_text
        return render_template('index.html', events=events)

@app.route('/new_character', methods=['POST', 'GET'])
def new_character():
    
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
    return render_template('new_character.html', ProfessionChoices=profession_choices, Stats=stats)


if __name__ == '__main__':
    app.run(debug=True)


# host='127.0.0.1', port=8080, 
