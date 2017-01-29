from flask import Response, Flask, jsonify, make_response, url_for, render_template, \
    send_from_directory, request, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from pymongo import MongoClient, DESCENDING, IndexModel, TEXT
from datetime import datetime, timedelta
from forms import ToolLogForm, LoginForm, RegistrationForm, SearchForm
import os
from app_config import *
from flask_login import LoginManager, login_required, login_user, current_user,logout_user
from User import User
from bson.objectid import ObjectId
#https://flask-login.readthedocs.io/en/latest/#installation
#understanding url_for https://www.youtube.com/watch?v=Ofy_jRHE3no

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.loging_view = 'login'
Bootstrap(app)
bcrypt = Bcrypt(app)

app.config.update(SECRET_KEY= update_sec_key())

'''
Defs
'''
def check_admin(user):
    admins = ["Brandon"]
    #create a for loop that iterates through 
    for admin in admins:
        if admin == user:
            return True
    return False

def delete_from_db(_id):
    print(_id)
    print(str(_id))
    print(hobby_coll.find_one({"_id": ObjectId(_id)}))
    hobby_coll.remove({"_id": ObjectId(_id), "username":current_user.get_id() })
    print("deleted %s" % (_id))
    #return "deleted %s" % (_id)

@login_required
def get_items():
    username = current_user.get_id()
    user_items = []

    for item in hobby_coll.find({'username': username}):
        user_items.append(item)
    print(user_items)

    tags = ""
    return user_items

@login_manager.user_loader
def load_user(username):  
    u = user_coll.find_one({"username": username})
    if not u:
        return None
    
    return User(u['username'])

@login_required
def search_db(name_query):
    #name_query = name_query.split(" ")
    result = []
    #for word in name_query:
    hobby_coll.create_index([('name',TEXT)])
    for document in hobby_coll.find( { '$text': { '$search': name_query}, 'username':current_user.get_id() } ):
        result.append(document)
    print(result)
    return result

'''
Routes
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        user_items = get_items()
    else:
        user_items = None
    return render_template('index.html', user_items =user_items)

@login_required
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    print(str(app.open_session(request)))
    form = ToolLogForm(request.form)
    
    if request.method == 'POST' and form.validate():
        name = form.name.data
        bin_number = form.bin_number.data
        drawer_number = form.drawer_number.data
        comment = form.comment.data
        tags = form.tags.data
        username = current_user.get_id()
        created_date_time = datetime.utcnow()
        modified_date_time = datetime.utcnow()
        tags = tags.split(" ")
        
        data_to_log = {
            'name':name,
            'bin_number': bin_number,
            'drawer_number': drawer_number,
            'comment': comment,
            'tags': tags,
            'username': username,
            'created_date_time': created_date_time,
            'modified_date_time': modified_date_time
            
        }

        hobby_coll.insert(data_to_log)
        return redirect(url_for('add_item'))
    return render_template('add_item.html',form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/search', methods=['GET','POST'])
def search():
    data = None
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        name_query = form.name.data
        data = "No Data"

        data = search_db(name_query)
        print(data)

        return render_template('search.html', data=data, form=form)
    return render_template('search.html',form=form)

@app.route('/edit/<_id>', methods=['GET', 'POST'])
def edit(_id):
    print(hobby_coll.find_one({"_id": ObjectId(_id)}))
    print(str(app.open_session(request)))
    form = ToolLogForm(request.form)
    data = hobby_coll.find_one({"_id": ObjectId(_id)})

    old_name = data['name']
    old_drawer_number = data['drawer_number']
    old_bin_number = data['bin_number']
    old_comment = data['comment']
    old_tags = data['tags']
    old_tags = " ".join(old_tags)

    if request.method == 'GET':
        form.name.data = old_name
        form.bin_number.data = old_drawer_number
        form.drawer_number.data = old_bin_number
        form.comment.data = old_comment
        form.tags.data = old_tags

    if request.method == 'POST' and form.validate():
        update_id = ObjectId(data['_id'])
        print(update_id)

        name = form.name.data
        bin_number = form.bin_number.data
        drawer_number = form.drawer_number.data
        comment = form.comment.data
        tags = form.tags.data
        tags = tags.split(" ")
        modified_date_time = datetime.utcnow()
        
        
        data_to_log = {
            'name':name,
            'bin_number': bin_number,
            'drawer_number': drawer_number,
            'comment': comment,
            'tags': tags,
            'modified_date_time': modified_date_time,
        }

        
        hobby_coll.update_one({'_id': update_id}, {"$set": data_to_log})
        return redirect(url_for('index'))

    return render_template('edit.html',form=form, data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():

        #form data loader
        form_email = form.login_email.data
        form_password = form.password.data

        #DB user loader
        if(user_coll.find_one({'email':form_email})):   
            user = user_coll.find_one({'email':form_email})
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
                    #return render #render_template('index.html')
                else:
                    error = "Invalid email or password."
            print(user_email)
        else:
            error = "Invalid email or password"

    return render_template('login.html', form=form, error = error)

@app.route("/settings")
@login_required
def settings():
    pass

@app.route("/admin")
@login_required
def admin():
    if check_admin(current_user.get_id()):
        return render_template('admin.html')
    else:
        flash('VERFICATION FAILED: You are not an administrator.')
        return redirect(url_for('index'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    user_coll = db['user-database']
    form = RegistrationForm(request.form)
    error = None
    
    if request.method == 'POST' and form.validate():
        username = form.login_username.data
        email = form.login_email.data
        password_hashed = bcrypt.generate_password_hash(form.password.data)

        if (user_coll.find_one({'email':email})) == None:
            if (user_coll.find_one({'username': username})) == None:
                data_to_log = {
                    'username': username,
                    'email': email,
                    'password': password_hashed
                }
                user_coll.insert(data_to_log)
                flash('You were successfully registered!')
                return redirect(url_for('index'))
            else:
                error = "Username taken"
        else:
            error = "Email already in use"
        
    return render_template('register.html', form=form,error = error)

@app.route('/view', methods=['GET', 'POST'])
@login_required
def view():

    #find current user logged and return records of that users inputs
    username = current_user.get_id()
    user_items = []

    for item in hobby_coll.find({'username': username}):
        user_items.append(item)
    print(user_items)

    tags = ""

    return render_template('view.html', user_items = user_items)

@app.route('/delete/<_id>', methods=['GET', 'POST'])
@login_required
def delete(_id):
    delete_from_db(_id)
    return redirect(url_for('view'))

if __name__ == '__main__':
    #app.run(debug=True)
    # get port assigned by OS else set it to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)