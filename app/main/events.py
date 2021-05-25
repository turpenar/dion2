from flask import session
from flask_socketio import send, emit, join_room, leave_room, rooms
from flask_login import login_user, login_required, logout_user, current_user

from app import socketio, db

from app.main import actions, player, world

@socketio.on('connect')
def test_connect():
    emit('after_connect', {'data': 'connected'})
    # if current_user.character_1:
    #     current_user.character_1.room = world.tile_exists(x=current_user.character_1.location_x, y=current_user.character_1.location_y, area=current_user.character_1.area)
    #     if not current_user.character_1.room.room_filled:
    #         current_user.character_1.room.fill_room(character=current_user.character_1)
    #     join_room(current_user.character_1.room.room_number)
    #     emit('after_connect', {'data': 'You are connected to the server. You are connected as ' 
    #                      + current_user.character_1.first_name 
    #                      + '<br>'
    #                      + current_user.character_1.room.intro_text()}) 
        
    # else:
    #     emit('after_connect', {'data': 'You have not yet set up a character.'})
    
@socketio.event
def game_action(msg):
    action = msg['data']
    print(action)
    emit('game_event', {'data': action})
    print(rooms())
#    current_user.character_1.room = world.tile_exists(x=current_user.character_1.location_x, y=current_user.character_1.location_y, area=current_user.character_1.area)
#    start_room_number = current_user.character_1.room.room_number
#    action_result = actions.do_action(action_input=msg['data'], character=current_user.character_1)
#    if action_result['character_output']:
#        emit('message', {'data': action_result['character_output']})
#    if action_result['room_change']['room_change_flag'] == True:
#            leave_room(action_result['room_change']['old_room'])
#            join_room(action_result['room_change']['new_room'])
#    if action_result['room_output']:
#        for room in action_result['room_output']:
#            emit('message', {'data': action_result['room_output'][room]}, room=room, include_self=False)
#    if action_result['status_window']:
#        emit('status_window_print', {'data': action_result['status_window']})
#    emit('message', {'data': 'You joined:  ' + ','.join(str(rooms()))})
#    db.session.commit()
