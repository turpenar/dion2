from flask import session
from flask_socketio import send, emit
from app import socketio

@socketio.event
def connect():
    emit('message', {'data': 'You are connected to the server.'})
    
@socketio.event
def game_action(msg):
    emit('message', {'data': msg['data']})
    
def game_event(game_event_text):
    socketio.emit('game_event_print', {'data': game_event_text})

def status_window(status_window_text):
    socketio.emit('status_window_print', {'data': status_window_text})
