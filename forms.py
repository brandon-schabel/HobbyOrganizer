from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators

class ToolLogForm(Form):
    name = StringField(u'Item Name', validators=[validators.input_required()])
    bin_number = IntegerField(u'Bin', validators=[validators.input_required()])
    drawer_number = IntegerField(u'Drawer', validators=[validators.input_required()])
    comment = StringField(u'Comment', validators=[])
    tags = StringField(u'Tags', validators=[])

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

class SearchForm(Form):
    name = StringField(u'Search Item Name', validators=[validators.input_required()])