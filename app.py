from flask import Response, Flask, jsonify, make_response, url_for, render_template, \
    send_from_directory, request
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from bson import json_util
from time import sleep, time
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
from json import dumps
import sys
import os
from forms import ToolLogForm, LoginForm, RegistrationForm
from app_config import *
from session_mongo import MongoSessionInterface, MongoSession

app = Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
app.session_interface = MongoSessionInterface(db=config['db_client_name'], host=config['client_url'], port=int(config['client_port']),collection=config['session_db'])

print(str(app.session_interface))

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = ToolLogForm(request.form)
    
    if request.method == 'POST' and form.validate():
        name = form.name.data
        bin_number = form.bin_number.data
        drawer_number = form.drawer_number.data
        comment = form.comment.data
        tags = form.tags.data
        username = form.username.data
        current_date_time = datetime.utcnow()
        tags = tags.split(" ")
        
        data_to_log = {
            'name':name,
            'bin_number': bin_number,
            'drawer_number': drawer_number,
            'comment': comment,
            'tags': tags,
            'username': username,
            'current_date_time': current_date_time
        }

        tool_db.insert(data_to_log)
    return render_template('index.html',form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.username.data
        password_hashed = bcrypt.generate_password_hash(form.password.data)
        
        if(user_db.find_one({'email':email})):
            print('Found')
            
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user_db = db['user-database']
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        print('got to here')
        username = form.login_username.data
        email = form.login_email.data
        password_hashed = bcrypt.generate_password_hash(form.password.data)

        data_to_log = {
                'username': username,
                'email': email,
                'password': password_hashed
        }
        
        user_db.insert(data_to_log)
    else:
        print(str(form.validate()))
        
    return render_template('register.html', form=form)

@app.route('/view', methods=['GET', 'POST'])
def view():
    #find current user logged and return records of that users inputs
    username = "Brandon"
    my_array = []

    for item in tool_db.find({'username': username}):
        my_array.append(item)
    print(my_array)
    return str(my_array)


if __name__ == '__main__':
    #app.run(debug=True)
    # get port assigned by OS else set it to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)