from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from wtforms.fields import StringField, SelectField,\
    SubmitField, PasswordField, FieldList, DateField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from flask_wtf import FlaskForm


from app import db, login_manager


class SurveyForm(FlaskForm):
    """ User survey information """
    username_entry = StringField("Username",
                                 [validators.InputRequired(
                                     "Please enter a username:")])
    password_entry = PasswordField("Password",
                                   [validators.InputRequired(
                                     "Please enter a password:")])
    first_name_entry = StringField("First Name",
                                   [validators.InputRequired(
                                     "Please enter your first name:")])
    last_name_entry = StringField("Last Name",
                                  [validators.InputRequired(
                                     "Please enter your last name:")])
    email_entry = EmailField("Email", [validators.InputRequired(
                                "Please enter your email address."),
                               validators.Email(
                                 "Please enter your email address.")])

    age_entry = SelectField('Age',
                            choices=[('under18', 'Under 18'),
                                     ('18_24', '18 - 24'),
                                     ('25_34', '25 - 34'),
                                     ('35_44', '35 - 44'),
                                     ('45_54', '45 - 54'),
                                     ('55_64', '55 - 64'),
                                     ('65_74', '65 - 74'),
                                     ('75_84', '75 - 84'),
                                     ('older_85', '85 or older')],
                            validators=[validators.InputRequired(
                                "Please enter a choice")])

    food_entry = SelectField('Rate your interest' +
                             ' in "Food and Drinks" experiences: ',
                             choices=[("5", 'Very Interested'),
                                      ("4", 'Interested'),
                                      ("3",
                                      'Neither'),
                                      ("2", 'Not really interested'),
                                      ("1", 'Not interested at all')],
                             validators=[validators.InputRequired(
                                 "Please enter a choice")])

    nightlife_entry = SelectField('Rate your interest ' +
                                  'in "Night Life" experiences: ',
                                  choices=[("5",
                                            'Very Interested'),
                                           ("4", 'Interested'),
                                           ("3",
                                            'Neither'),
                                           ("2", 'Not really interested'),
                                           ("1", 'Not interested at all')],
                                  validators=[validators.InputRequired(
                                        "Please enter a choice")])

    nature_entry = SelectField('Rate your interest in "Nature" ' +
                               'experiences: ',
                               choices=[("5", 'Very Interested'),
                                        ("4", 'Interested'),
                                        ("3",
                                         'Neither'),
                                        ("2", 'Not really interested'),
                                        ("1", 'Not interested at all')],
                               validators=[validators.InputRequired(
                                   "Please enter a choice")])

    museums_entry = SelectField('Rate your interest in visiting museums: ',
                                choices=[("5", 'Very Interested'),
                                         ("4", 'Interested'),
                                         ("3",
                                          'Neither'),
                                         ("2", 'Not really interested'),
                                         ("1", 'Not interested at all')],
                                validators=[validators.InputRequired(
                                    "Please enter a choice")])

    landmarks_entry = SelectField('Rate your interest in visiting landmarks: ',
                                  choices=[("5", 'Very Interested'),
                                           ("4", 'Interested'),
                                           ("3",
                                            'Neither'),
                                           ("2", 'Not really interested'),
                                           ("1", 'Not interested at all')],
                                  validators=[validators.InputRequired(
                                      "Please enter a choice")])

    music_entry = SelectField('Rate your interest in listening to concerts: ',
                              choices=[("5", 'Very Interested'),
                                       ("4", 'Interested'),
                                       ("3",
                                        'Neither'),
                                       ("2", 'Not really interested'),
                                       ("1", 'Not interested at all')],
                              validators=[validators.InputRequired(
                                  "Please enter a choice")])

    performing_entry =\
        SelectField('Rate your interest in Performing & Visual Arts: ',
                    choices=[("5", 'Very Interested'),
                             ("4", 'Interested'),
                             ("3",
                              'Neither'),
                             ("2", 'Not really interested'),
                             ("1", 'Not interested at all')],
                    validators=[validators.InputRequired(
                        "Please enter a choice")])

    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    """Log in fields"""
    username_entry =\
        StringField("Username",
                    [validators.InputRequired(
                        "Please enter a username:")])
    password_entry =\
        PasswordField("Password",
                      validators=[validators.InputRequired(
                         "Please enter a password:")])
    submit = SubmitField("Submit")


class User(db.Model, UserMixin):
    """User object"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    age = db.Column(db.String(80), unique=False, nullable=False)

    food = db.Column(db.Integer, unique=False, nullable=False)
    nightlife = db.Column(db.Integer, unique=False, nullable=False)
    museums = db.Column(db.Integer, unique=False, nullable=False)
    nature = db.Column(db.Integer, unique=False, nullable=False)
    landmarks = db.Column(db.Integer, unique=False, nullable=False)
    music = db.Column(db.Integer, unique=False, nullable=False)
    performing = db.Column(db.Integer, unique=False, nullable=False)

    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password,
                 first_name, last_name, age,
                 food, nightlife, museums, nature,
                 landmarks, music, performing):

        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

        self.food = food
        self.nightlife = nightlife
        self.museums = museums
        self.nature = nature
        self.landmarks = landmarks
        self.music = music
        self.performing = performing

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TripForm(FlaskForm):
    """Trip survey information """
    name_entry =\
        StringField("Trip Name",
                    validators=[validators.InputRequired(
                        "Please enter a name for your trip:")])
    where_entry =\
        StringField("Where",
                    validators=[validators.InputRequired(
                        "Where are you going?")])
    start_date_entry =\
        DateField("Start Date",
                  validators=[validators.InputRequired("Start Date")],
                  format='%m-%d-%Y')
    end_date_entry = DateField("End Date",
                               format='%m-%d-%Y')

    # new field for adding users on trips by email
    party = StringField('party')

    submit = SubmitField("Submit")


class Trip(db.Model, UserMixin):
    """Trip object"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    where = db.Column(db.String(80), unique=False, nullable=False)
    creator = db.Column(db.String(80), unique=False, nullable=False)
    # invite_list = db.Column(db.String(80), unique=False, nullable=False)
    start_date = db.Column(db.Date(), unique=False, nullable=False)
    end_date = db.Column(db.Date(), unique=False, nullable=False)

    def __init__(self, name, where, start_date, end_date, creator):

        self.name = name
        self.where = where
        self.creator = creator
        # self.invite_list = invite_list
        self.start_date = start_date
        self.end_date = end_date


db.create_all()
db.session.commit()

# user_loader :
# This callback is used to reload the user object
# from the user ID stored in the session.
@login_manager.user_loader
def load_user(id):
    """load current user based on their ID"""
    return User.query.get(int(id))
