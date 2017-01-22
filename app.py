from flask import Response, Flask, jsonify, make_response, url_for, render_template, \
    send_from_directory, request, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from datetime import datetime, timedelta
from forms import ToolLogForm, LoginForm, RegistrationForm
import os
from app_config import *
from flask_login import LoginManager, login_required, login_user
from User import User
#https://flask-login.readthedocs.io/en/latest/#installation

app = Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config.update(SECRET_KEY= update_sec_key())

@login_manager.user_loader
def load_user(username):  
    u = user_db.find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    print(str(app.open_session(request)))
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
        form_email = form.login_email.data
        form_password = form.password.data

        print(user_db.find_one({'email':form_email}))
        #user_email = (user_db.find_one({'email':email}))['email']
        user = user_db.find_one({'email':form_email})
        user_email = user['email']
        user_pass = user['password']
        username = user['username']

        print(user_email)
        print(form_email)
        print(user_pass)
        print(form_password)

        if(user_email == form_email):
            if(bcrypt.check_password_hash(user_pass, form_password)):
                user_obj = User(username)
                login_user(user_obj)
                #add flash message 
                print('my balls')
                next = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See http://flask.pocoo.org/snippets/62/ for an example.
                '''
                if not is_safe_url(next):
                    return flask.abort(400)
                '''
                return '<h1> Yolo Swag </h1>' #render_template('index.html')
            else:
                print('didn\'t work')
        print(user_email)
        '''
        if(user_db.find_one({'email'}) == ):
            user = user_db.find({'email':email})
            print(user)

            print('Found')
        '''
    return render_template('login.html', form=form)

@app.route("/settings")
@login_required
def settings():
    pass

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somewhere)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user_db = db['user-database']
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        print('got to here')
        username = form.login_username.data
        email = form.login_email.data
        print(form.password.data)
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
@login_required
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
    app.run(host='0.0.0.0', port=port,debug=True)