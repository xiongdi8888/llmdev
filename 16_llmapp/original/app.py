import os
import sys
import uuid
from dotenv import load_dotenv
load_dotenv('.env')
from flask import Flask, render_template, request, make_response, session
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from original.graph import get_bot_response, get_messages_list, memory

app = Flask(__name__)
app.secret_key = os.environ['ENV_APP_KEY']

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())
    if request.method == 'GET':
        memory.storage.clear()
        return make_response(render_template('index.html', messages=[]))
    user_message = request.form['user_message']
    get_bot_response(user_message, memory, session['thread_id'])
    messages = get_messages_list(memory, session['thread_id'])
    return make_response(render_template('index.html', messages=messages))

@app.route('/clear', methods=['POST'])
def clear():
    session.pop('thread_id', None)
    memory.storage.clear()
    return make_response(render_template('index.html', messages=[]))

if __name__ == '__main__':
    app.run(debug=True)
