from flask import session
from flask_socketio import send, emit
from app import socketio

from app.main import actions, player

@socketio.event
def connect():
    emit('message', {'data': 'You are connected to the server.'})
    
@socketio.event
def game_action(msg):
    emit('message', {'data': msg['data']})
    actions.do_action(action_input=msg['data'], character=player.character)
    
def game_event(game_event_text):
    socketio.emit('game_event_print', {'data': game_event_text})

def status_window(status_window_text):
    socketio.emit('status_window_print', {'data': status_window_text})
