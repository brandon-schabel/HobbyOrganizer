from flask import Response, Flask, jsonify, make_response, url_for, render_template, \
    send_from_directory, request
from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators
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
import configparser

app = Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)


def ConfigSectionMap(section):
    config = configparser.ConfigParser()
    config.read("./config.ini")
    dict1 = {}
    #sections are defined in config.ini and are listed as [NameHere]
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section,option)
            if dict1[option] == -1:
                DebugPrint("Skip: %s" % option)
        except:
            print("Exception on %s!" % option)
            dict1[option] = None
    return dict1

config = ConfigSectionMap('database_config')

client = MongoClient(config['client_url'], int(config['client_port']))
# connecting to our mlab database
db = client[config['db_client_name']]
db.authenticate(config['db_user'], config['db_pass'])

tool_db = db[config['tool_db']]
user_db = db[config['user_db']]

class ToolLogForm(Form):
    name = StringField(u'Item Name', validators=[validators.input_required()])
    bin_number = IntegerField(u'Bin', validators=[validators.input_required()])
    drawer_number = IntegerField(u'Drawer', validators=[validators.input_required()])
    comment = StringField(u'Comment', validators=[])
    tags = StringField(u'Tags', validators=[])
    user = StringField(u'User', validators=[])

class LoginForm(Form):
    login_email = StringField(u'Email',validators=[])
    password = PasswordField(u'Password', validators=[])

class RegistrationForm(Form):
    login_username = StringField (u'Username', validators=[validators.input_required()])
    login_email = StringField (u'Email', validators=[validators.input_required()])#validators.Email(), validators.EqualTo('confirm_email', message='Emails must match')
    confirm_email = StringField(u'Repeat Email')
    password = PasswordField(u'Password', validators=[validators.input_required()])#, validators.EqualTo('confirm_pass', message='Passwords must match')
    confirm_pass = PasswordField(u'Repeat Password')
    #accept_tos = BooleanField(u'I accept the TOS', [validators.DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = ToolLogForm(request.form)
    
    if request.method == 'POST' and form.validate():
        name = form.name.data
        bin_number = form.bin_number.data
        drawer_number = form.drawer_number.data
        comment = form.comment.data
        tags = form.tags.data
        user = form.user.data
        current_date_time = datetime.utcnow()
        tags = tags.split(" ")
        
        data_to_log = {
            'name':name,
            'bin_number': bin_number,
            'drawer_number': drawer_number,
            'comment': comment,
            'tags': tags,
            'user': user,
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

    
if __name__ == '__main__':
    #app.run(debug=True)
    # get port assigned by OS else set it to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)