from flask import session
from flask_socketio import send, emit, join_room, leave_room, rooms
from app import socketio

from app.main import actions, player

@socketio.event
def connect():
    emit('message', {'data': 'You are connected to the server.'})
    
@socketio.event
def game_action(msg):
    emit('message', {'data': msg['data']})
    start_room_number = player.character.room.room_number
    action_result = actions.do_action(action_input=msg['data'], character=player.character)
    if action_result['character_output']:
        emit('message', {'data': action_result['character_output']})
    if action_result['room_change']['room_change_flag'] == True:
            leave_room(action_result['room_change']['old_room'])
            join_room(action_result['room_change']['new_room'])
    if action_result['room_output']:
        for room in action_result['room_output']:
            emit('message', {'data': action_result['room_output'][room]}, room=room, include_self=False)
    if action_result['status_window']:
        emit('status_window_print', {'data': action_result['status_window']})
    emit('message', {'data': 'You joined:  ' + ','.join(str(rooms()))})
    
def game_event(game_event_text):
    socketio.emit('game_event_print', {'data': game_event_text})

def status_window(status_window_text):
    socketio.emit('status_window_print', {'data': status_window_text})
