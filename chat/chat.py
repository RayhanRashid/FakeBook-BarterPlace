# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# from datetime import datetime

# from app import app

# socketio = SocketIO(app)



# """

# working progress ! :(

# """

# # sample chat, change latr using mongodb
# chats = {} # {sender: {receiver: [(message, timestamp), ... ]}}

# '''
# note: remeber to change chats (db) operations!!
# '''
# @app.route('/chat')
# def chat():
#     return render_template('chat.html')

# @socketio.on('send_message')
# def handle_message(data):

#     sender = "" # get username from db/cookie
#     receiver = data["receiver"]   
#     message = data["message"]

#     # optional timestamp
#     timestamp = datetime.utcnow().isoformat() + "Z"     # time message is being sent

#     # create chatroom if room does not exist
#     if receiver not in chats[sender]:
#         chats[sender][receiver] = []    # create new chat
#     if sender not in chats[receiver]:
#         chats[receiver][sender] = []    # create new chat

#     chats[sender][receiver].append((message, timestamp))    # change to mongodb operation!
#     chats[receiver][sender].append((message, timestamp))    # change 
    
#     # emit chat to connected client
#     emit('receive_message',
#          {
#              'sender': sender,
#              'message': message,
#              'timestamp': timestamp
#          }, room=receiver)


# @socketio.on('get_messages')
# def get_messages(data):
#     sender = ""   # get from db/cookie
#     receiver = data["receiver"]
#     messages = chats[sender].get(receiver, [])         # change to mongodb op.

#     # send msg back to client/room
#     emit("chat_history", messages)