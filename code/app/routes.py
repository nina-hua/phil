from app import application, db, classes
from flask import render_template, redirect, url_for, Blueprint, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from flask_login import LoginManager
from config import Config
import pandas as pd
import numpy as np
import random
from os.path import expanduser
import psycopg2


@application.route('/index')
@application.route('/')
def index():
    """Home page"""
    loggedin = current_user.is_authenticated  # is the user logged in?
    return (render_template("index.html", loggedin=loggedin))


@application.route('/register', methods=['GET', 'POST'])
def register():
    """Sign up"""
    if current_user.is_authenticated:
        return '<h1> Error: User already logged in. </h1>'
    form = classes.SurveyForm()
    if form.validate_on_submit():
        username = form.username_entry.data
        password = form.password_entry.data
        first_name = form.first_name_entry.data
        last_name = form.last_name_entry.data
        email = form.email_entry.data
        age = form.age_entry.data

        food = form.food_entry.data
        nightlife = form.nightlife_entry.data
        nature = form.nature_entry.data
        museums = form.museums_entry.data
        landmarks = form.landmarks_entry.data
        music = form.music_entry.data
        performing = form.performing_entry.data

        user_count = classes\
            .User\
            .query\
            .filter_by(username=username)\
            .count() +\
            classes.User.query.filter_by(email=email).count()

        if (user_count > 0):
            return '<h1> Error - Existing user : ' +\
                username + ' or ' + email + '</h1>' +\
                '<p> Please <a href="/register">try again.</a></p>'

        else:
            user = classes.User(username=username,
                                email=email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name,
                                age=age,
                                food=food,
                                nightlife=nightlife,
                                museums=museums,
                                nature=nature,
                                landmarks=landmarks,
                                music=music,
                                performing=performing)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('my_account'))
    return render_template('register.html', form=form)

# @application.route('/thanks', methods=['GET', 'POST'])
# def thanks():
#     return render_template('thanks.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    """Existing user login"""
    if current_user.is_authenticated:
        return '<h1> Error: User already logged in. </h1>'
    # Have user enter their email and password
    log_form = classes.LoginForm()
    if log_form.validate_on_submit():
        username = log_form.username_entry.data
        password = log_form.password_entry.data
        # Look for it in the database.
        user = classes.User.query.filter_by(username=username).first()

        # Login and validate the user.
        if user is not None and user.check_password(password):
            login_user(user)
            # redirect user to the secret page route
            return redirect(url_for('my_account'))

        else:
            flash('Invalid username and password combination!')

    return render_template('login.html', form=log_form)


@application.route('/logout')
@login_required
def logout():
    """Allow a logded in user to logout"""

    logout_user()

    loggedin = current_user.is_authenticated  # is the user logged in?
    return (render_template("index.html", loggedin=loggedin))


# redirect unauthorize users to login page
@application.errorhandler(401)
def unauthorize(e):
    """route unauthorize users to the login page"""
    return redirect(url_for('login'))


# once logged in, login_required will fetch active user information
@application.route('/my_account')
@login_required
def my_account():
    """Logged in user account page"""
    trips_results = classes.Trip.query.filter_by(creator=current_user.username).all()
    trip_names = [x.name for x in trips_results]
    return render_template('my_account.html',
                           name=current_user.first_name,
                           email=current_user.email,
                           trip_names=trip_names)


@application.route('/about_us')
def about_us():
    """Shows about us page"""
    return render_template('aboutus.html')


@application.route('/create_trip', methods=['GET', 'POST'])
@login_required
def create_trip():
    """Allow a user to create a new trip"""
    if not current_user.is_authenticated:
        return '<h1> Error: Log in to create trip. </h1>'
    form = classes.TripForm()
    if form.validate_on_submit():
        name = form.name_entry.data
        where = form.where_entry.data
        creator = current_user.username
        # invite_list = form.usernames_entry.data
        start_date = form.start_date_entry.data
        end_date = form.end_date_entry.data

        trip_count = classes.Trip.query.filter_by(name=name).count()

        if (trip_count > 0):
            flash('ERROR: Trip ' + name + ' already exist. Please make a unique trip name.')
            return render_template('create_trip.html', form=form)

        else:
            party_username = [creator]

            party_entry = form.party.data
            if party_entry.strip() != '':  # other users in trip
                # look up username of emails provided
                party_list = party_entry.split(',')
                for p in party_list:
                    p = p.strip()
                    found = classes.User.query.filter_by(email=p).count()
                    if found == 0:  # if user not found, throw error
                        flash('ERROR: Email ' + p + ' not found. Please check email is correct.')
                        return render_template('create_trip.html', form=form)
                    else:
                        party_row = classes.User.query.filter_by(email=p).first()
                        party_username.append(party_row.username)

            # add trip for all users
            for creator in party_username:
                trip_row = classes.Trip(name=name, where=where, creator=creator,
                                    start_date=start_date, end_date=end_date)
                db.session.add(trip_row)
                db.session.commit()

            return redirect(url_for('scheduler', t_name=name))

    return render_template('create_trip.html', form=form)


@application.route('/trip', methods=['GET', 'POST'])
@login_required
def trip():
    t_name = request.args['t_name']
    u_name = current_user.username
    # user must belong to trip to see trip
    if not t_belong(t_name, u_name):
        return f'<p>Trip {t_name} does not belong to you</p>'

    trip_results = classes.Trip.query.filter_by(name=t_name).all()
    current_schedule = get_schedule(t_name, True)
    return render_template('trip_details.html', name=t_name, trip=trip_results, current_schedule=current_schedule)


@application.route('/scheduler',  methods=['GET', 'POST'])
@login_required
def scheduler():
    t_name = request.args['t_name']
    u_name = current_user.username

    # user must belong to trip to see trip
    if not t_belong(t_name, u_name):
        return f'<p>Trip {t_name} does not belong to you</p>'

    trip_results = classes.Trip.query.filter_by(name=t_name).all()

    # nina: get trip recommendations based on trip_results
    travelers = []
    start_date = trip_results[0].start_date  # get the start_date for one entry
    end_date = trip_results[0].end_date  # get the end_date for one entry
    # appending all creators for a trip to a list
    for row in trip_results:
        # travelers.append(row.creator)
        score = classes.User.query.filter_by(username=row.creator).first()
        pref = (score.food, score.nightlife, score.museums, score.nature,
                score.landmarks, score.music, score.performing)
        travelers.append(pref)

    con = Config.SQLALCHEMY_DATABASE_URI  # get connection string to database
    filtered_events_df = query_events(start_date, end_date, con)  # query events table

    # return "<p>" + str(travelers) + "</p>"

    recos = rule_rec(event_df=filtered_events_df, user_ratings=travelers, N=30)

    # populating the schedule table
    engine = connect_to_db()

    for rec in recos:

        event_info = (t_name, rec["id"], False)  # False because person hasn't selected
        insert_recs(engine, event_info)
    current_schedule = get_schedule(t_name, True)
    return render_template('options.html', events=recos, t_name=t_name, current_schedule=current_schedule)


@application.route('/add_event',  methods=['GET', 'POST'])
@login_required
def add_event():
    """add event to the schedule table for trip"""
    event_id = request.args['event_id']
    t_name = request.args['t_name']

    # connect to db
    engine = connect_to_db()

    # insert event to schedule table
    cmd = f"""UPDATE public.schedule 
    SET selected = TRUE 
    WHERE (trip_name = '{t_name}') AND (event_id = {event_id});"""
    with engine.cursor() as cur:
        cur.execute(cmd)
        engine.commit()

    # get un-added events
    final_recs = get_schedule(t_name, False)
    current_schedule = get_schedule(t_name, True)

    return render_template('options.html', events=final_recs, t_name=t_name, current_schedule=current_schedule)


@application.route('/del_event',  methods=['GET', 'POST'])
@login_required
def del_event():
    """add event to the schedule table for trip"""
    event_id = request.args['event_id']
    t_name = request.args['t_name']

    # connect to db
    engine = connect_to_db()

    # insert event to schedule table
    cmd = f"""UPDATE public.schedule 
    SET selected = FALSE 
    WHERE (trip_name = '{t_name}') AND (event_id = {event_id});"""
    with engine.cursor() as cur:
        cur.execute(cmd)
        engine.commit()

    # get un-added events
    final_recs = get_schedule(t_name, False)
    current_schedule = get_schedule(t_name, True)

    return render_template('options.html', events=final_recs, t_name=t_name, current_schedule=current_schedule)


# helper functions
def get_schedule(t_name, suggested=False):
    """query the schedule table to get
    either suggested schedule (suggested=True)
    or current schedule (suggested=False)"""

    # connect to db
    engine = connect_to_db()

    # get events
    cmd = f"""SELECT event_id 
     FROM public.schedule
     WHERE trip_name = '{t_name}' AND selected IS {suggested};"""
    with engine.cursor() as cur:
        cur.execute(cmd)
        engine.commit()
        results = cur.fetchall()
    # prepare data to be re-render
    schedule = list()
    for event in results:
        event_id = event[0]
        cmd = f"""SELECT id, event_name, event_desc, event_url, event_start, event_category
         FROM public.events WHERE id = {event_id};"""
        with engine.cursor() as cur:
            cur.execute(cmd)
            engine.commit()
            rec = cur.fetchone()
        r_dict = event_row_to_dic(rec)
        schedule.append(r_dict)

    return schedule


def connect_to_db():
    """start a psycopg2 connection to db
    return engine"""
    rds_key = read_key('/rds_key')
    engine = psycopg2.connect(
        database="phil_app",
        user="phil",
        password=rds_key,
        host="phil-app-db.cparuupfbjxx.us-west-2.rds.amazonaws.com",
        port='5432'
    )
    return engine


def event_row_to_dic(rec):
    """converts a row from the event table to a dictionary"""
    r_dict = dict()
    r_dict["id"] = rec[0]
    r_dict["event_name"] = rec[1]
    r_dict["event_desc"] = rec[2]
    r_dict["event_url"] = rec[3]
    r_dict["event_start"] = rec[4]
    r_dict["event_category"] = rec[5]

    return r_dict

def rule_rec(event_df, user_ratings, N):
    """
    Create event recommendations based on average of scores
    event_df: Pandas dataframe of queried events
    user_ratings: list of user ratings
    N: number of recommendations we would output
    output: list of dictionaries containing recommendation info
    """
    recs_dict = {}

    # assign group_pref according to if group of users or one user
    if len(user_ratings) > 1:
        prefs = [list(x) for x in zip(*user_ratings)]  # transpose the list
        group_pref = [np.mean(row) for row in prefs]  # get average preference
    else:
        group_pref = user_ratings[0]

    # calculating number of recommendations to make per category
    group_sum = sum(group_pref)
    num_recs = [np.round((pref / group_sum) * N) for pref in group_pref]

    # putting category, number of recs into dictionary
    for category, k in zip(['food', 'nightlife', 'museums', 'nature', 'landmarks', 'music', 'performing'], num_recs):
        recs_dict[category] = k

    # if the sum of recs does not equal N then add or subtract from the highest ranking category
    rec_sum = sum(recs_dict.values())
    if rec_sum != N:
        # get highest ranking key
        high_key = sorted(recs_dict.items(), key=lambda kv: -kv[1])[0][0]
        delta = np.abs(rec_sum - N)
        if rec_sum > N:
            # subtract from the top ranking if there are more than the recs requested
            recs_dict[high_key] -= delta
        else:
            # add to top ranking if missing recs
            recs_dict[high_key] += delta

    # make a list of recommendations based on dictionary
    # select events at random
    rec_list = []
    for cat, k in recs_dict.items():
        if cat == 'food':
            cat_df = event_df[(event_df['event_category'] == 'Food') |
                              (event_df['event_category'] == 'Food & Drink')]
        elif cat == 'nightlife':
            cat_df = event_df[event_df['event_category'] == 'nightlife']
        elif cat == 'museums':
            cat_df = event_df[event_df['event_category'] == 'Museum']
        elif cat == 'nature':
            cat_df = event_df[(event_df['event_category'] == 'Outdoor') |
                              (event_df['event_category'] == 'Travel & Outdoor')]
        elif cat == 'landmarks':
            cat_df = event_df[event_df['event_category'] == 'Landmark']
        elif cat == 'music':
            cat_df = event_df[event_df['event_category'] == 'Music']
        else:
            cat_df = event_df[event_df['event_category'] == 'Performing & Visual Arts']

        # if the number of wanted recs is greater than number of rows in df, return all rows in df
        if len(cat_df) < k:
            rand_recs = cat_df.values
        else:
            rand_recs = cat_df.sample(n=int(k)).values

        # unnest the list of recommendations
        if len(rand_recs) > 1:
            for rec in rand_recs:
                rec_list.append(rec)
        else:
            rec_list.append(rand_recs[0])

    final_recs = []
    for rec in rec_list:
        # dictionary object to hold information
        r_dict = {}
        r_dict["id"] = rec[0]
        r_dict["event_name"] = rec[1]
        r_dict["event_desc"] = rec[2]
        r_dict["event_url"] = rec[3]
        r_dict["event_start"] = rec[4]
        r_dict["event_category"] = rec[7]
        final_recs.append(r_dict)

    return final_recs


def query_events(start_date, end_date, con):
    """
    query the events table based on the start_date and end_date
    """
    sq = """SELECT * FROM public.events
        WHERE (event_start IS NULL AND event_end IS NULL)
           OR ( '{0}' <= event_start AND '{1}' >= event_end )
           OR ( ('{0}' <= event_start AND '{1}' > event_start) AND event_end IS NULL )
           OR ( ('{0}' <= event_end AND '{1}' >= event_end) AND event_start IS NULL );""".format(start_date, end_date)

    query_results = pd.read_sql_query(sq, con)
    return query_results


def t_belong(t_name, u_name):
    """user must belong to trip to see trip"""
    belongs = classes.Trip.query.filter_by(creator=u_name, name=t_name).count()
    return belongs != 0  # if result is not 0, then trip does belong


def read_key(fname):
    """reads in secret key from file
    assumes fname is at base of EC2"""
    with open(expanduser("~") + fname, 'r') as f:
        key = f.readline().strip()
    return key


def insert_recs(engine, e):
    """given a database connection and recommendation, insert into the schedule table"""

    cols = "(trip_name, event_id, selected)"

    with engine.cursor() as cur:
        cmd1 = f"""SELECT count(*) FROM public.schedule
                WHERE trip_name = '{e[0]}' AND event_id = {e[1]};"""
        cur.execute(cmd1)
        engine.commit()
        output = cur.fetchone()

        if output[0] == 0:
            cmd = f"""INSERT INTO public.schedule
                {cols} VALUES (%s, %s, %s)"""
            cur.execute(cmd, (e[0], e[1], e[2]))
            engine.commit()
