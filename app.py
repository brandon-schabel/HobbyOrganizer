from flask import Response, Flask, jsonify, make_response, url_for, render_template, \
    send_from_directory, request, url_for, redirect, flash 
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
#understanding url_for https://www.youtube.com/watch?v=Ofy_jRHE3no

app = Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.loging_view = 'login'
app.config.update(SECRET_KEY= update_sec_key())

@login_manager.user_loader
def load_user(username):  
    u = user_db.find_one({"username": username})
    if not u:
        return None
    
    return User(u['username'])

@app.route('/', methods=['GET', 'POST'])
def index():
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
    error = None
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():

        #form data loader
        form_email = form.login_email.data
        form_password = form.password.data

        #DB user loader
        user = user_db.find_one({'email':form_email})
        user_email = user['email']
        user_pass = user['password']
        username = user['username']

        #if form email is equal to the email from the database
        if(form_email == user_email):
            #if password from database is the same as the form password
            if(bcrypt.check_password_hash(user_pass, form_password)):
                user_obj = User(user['username'])
                login_user(user_obj)
                flash('You were successfully logged in')
                return redirect(url_for('view'))
                #add flash message 
                #http://flask.pocoo.org/docs/0.12/patterns/flashing/

                #next = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See http://flask.pocoo.org/snippets/62/ for an example.
                '''
                if not is_safe_url(next):
                    return flask.abort(400)
                '''
                return render #render_template('index.html')
            else:
                error = "Invalid email or password."
        print(user_email)

    return render_template('login.html', form=form, error = error)

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
    error = None
    
    if request.method == 'POST' and form.validate():
        username = form.login_username.data
        email = form.login_email.data
        password_hashed = bcrypt.generate_password_hash(form.password.data)

        if (user_db.find_one({'email':email})) == None:
            if (user_db.find_one({'username': username})) == None:
                data_to_log = {
                    'username': username,
                    'email': email,
                    'password': password_hashed
                }
                user_db.insert(data_to_log)
                flash('You were successfully registered!')
                return redirect(url_for('index'))
            else:
                error = "Username taken"
        else:
            error = "Email already in use"
        
    else:
        print(str(form.validate()))
        
    return render_template('register.html', form=form,error = error)

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