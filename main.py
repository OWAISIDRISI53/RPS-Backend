from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route('/')
def index():
    return "Rock-Paper-Scissors Backend Running!"

@socketio.on('create_room')
def create_room(data):
    room_code = data['room']
    rooms[room_code] = {'players': [], 'choices': {}}
    join_room(room_code)
    emit('room_created', {'room': room_code}, room=room_code)

@socketio.on('join_room')
def join_room_event(data):
    room_code = data['room']
    username = data['username']

    if room_code in rooms and len(rooms[room_code]['players']) < 2:
        rooms[room_code]['players'].append(username)
        join_room(room_code)
        emit('player_joined', {'players': rooms[room_code]['players']}, room=room_code)
    else:
        emit('error', {'message': 'Room is full or does not exist'})

@socketio.on('make_choice')
def make_choice(data):
    room_code = data['room']
    username = data['username']
    choice = data['choice']  # 'rock', 'paper', or 'scissors'

    rooms[room_code]['choices'][username] = choice

    if len(rooms[room_code]['choices']) == 2:
        players = list(rooms[room_code]['choices'].keys())
        choices = rooms[room_code]['choices']
        result = determine_winner(choices[players[0]], choices[players[1]])

        emit('game_result', {'choices': choices, 'result': result}, room=room_code)
        rooms[room_code]['choices'] = {}

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return 'Draw'
    if (choice1 == 'rock' and choice2 == 'scissors') or \
       (choice1 == 'scissors' and choice2 == 'paper') or \
       (choice1 == 'paper' and choice2 == 'rock'):
        return 'Player 1 Wins'
    return 'Player 2 Wins'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)