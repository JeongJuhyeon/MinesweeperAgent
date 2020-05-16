from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bimil'
socketio = SocketIO(app)

import AIController

thread = None

def background_thread():
    AIController.ai_start(socketio, web_client=True, bfs=True)

@socketio.on('connect')
def connect():
    socketio.emit('hello', {'Hello World': '1'})
    print('emitted connect')
    time.sleep(2)
    global thread
    thread = socketio.start_background_task(target=background_thread)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, port=12321)