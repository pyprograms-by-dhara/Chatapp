from flask import Flask,render_template,request,session,redirect,url_for
from flask_socketio import SocketIO,send,emit,join_room,leave_room
import random
from string import ascii_uppercase

app=Flask(__name__)
app.config['SECREAT_KEY']="DHARA@3511"
socketio=SocketIO(app)


rooms={}

def generate_room_code(length):
    while True:
        code=""
        for _ in range(length):
            code+=random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    print(code)
    return code
@app.route('/', methods=["POST", "GET"])
def home():
    session.clear()

    if request.method == "POST":
        name = request.form.get('name')
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)

        if not name:
            return render_template('chat1/chome.html', error="Name is required", code=code)

        if create != False:
            room_code = generate_room_code(5)
            new_room = {
                'members': 0,
                'messages': []
            }
            rooms[room_code] = new_room

        if join != False:
            # no code
            if not code:
                return render_template('chat1/chome.html', error="Please enter a room code to enter a chat room", name=name)
            # invalid code
            if code not in rooms:
                return render_template('chat1/chome.html', error="Room code invalid", name=name)

            room_code = code
        print(room_code)
        session['room'] = room_code
        session['name'] = name
        return redirect(url_for('room'))
    
    else:
        return render_template('chat1/chome.html')


@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')

    if name is None or room is None or room not in rooms:
        return render_template("chat1/chome.html")

    messages = rooms[room]['messages']
    return render_template('chat1/room.html', room=room, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    room=session.get('room')
    name=session.get('name')

    if name is None or room is None:
        return 

    if room not in rooms:
        leave_room(room)

    join_room(room)
    print(f"{name} joined room {room}")
    send({
        "sender":"",
        "message":f"{name} has entered the chat"
    },to=room)
    rooms[room]["members"]+=1

@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')
    if room not in rooms:
        return
    message = {
        "sender": name,
        "message": payload['data']
    }
    send(message, to=room)
    rooms[room]["messages"].append(message)

@socketio.on('disconnect')
def handle_disconnect():
    room=session.get("room")
    name=session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"]-=1
        if rooms[room]["members"]<=0:
            del rooms[room]

    send({
            "message":f"{name} has left the chat",
            "sender" : ""  
         },to=room)
        
    

if __name__=="__main__":
    app.secret_key='DHARA@2411'
    app.run(debug=True)
    socketio.run(app)
