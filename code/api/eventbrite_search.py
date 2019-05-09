import psycopg2
import requests
import json
import re
from os.path import expanduser


def table_exist(engine, table_name):
    """given an database connection and table,
    check if table exist in database. return true & false"""

    with engine.cursor() as cur:
        cmd = f"""select exists (select *
        from information_schema.tables
        where table_name='{table_name}');"""
        cur.execute(cmd)
        results = cur.fetchall()

    return results[0][0]


def insert_event(engine, e):
    """given a database connection and
    a tabular form of a eventbrite event,
    insert into the events table
    if event does not exit in table"""

    with engine.cursor() as cur:  # check if event exist already
        cmd = f"""SELECT count(*) FROM public.events
        WHERE ID = {e[0]};"""
        cur.execute(cmd)
        engine.commit()
        output = cur.fetchone()

    if output[0] == 0:  # need to add event to table, else do nothing
        cols = "(ID, event_name, event_desc, event_url," + \
               "event_start, event_end, is_free, event_category)"
        with engine.cursor() as cur:
            cmd = f"""INSERT INTO public.events
            {cols} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(cmd, (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7]))
            engine.commit()


def make_events(engine):
    """given a database connection,
    create an events table"""
    with engine.cursor() as cur:
        make_table = """CREATE TABLE public.events(
         ID bigserial PRIMARY KEY,
         event_name VARCHAR (255),
         event_desc TEXT,
         event_url TEXT,
         event_start DATE,
         event_end DATE,
         is_free BOOLEAN,
         event_category VARCHAR(255));"""
        cur.execute(make_table)
        engine.commit()


def clean_text(text):
    """given a string, remove any tabs"""
    try:
        clean = re.sub('\t', '. ', text)
        clean = re.sub('\n', '. ', clean)
        clean = re.sub("\'", '', clean)
        return clean
    except Exception:
        return text


def make_tabular_eb(event, cat_name):
    """given a json object from eventbrite api,
    manipulate results into tabular form"""
    idx = int(event['id'])
    name = clean_text(event['name']['text'])
    desc = clean_text(event['description']['text'])
    url = event['url']
    start = event['start']['local']
    end = event['end']['local']
    free = bool(event['is_free'])

    return (idx, name, desc, url, start, end, free, cat_name)


def get_events(categories):
    """using Eventbrites api
    given a dictionary:
        key: category id (specified by eventbrite)
        value: category names
    return list of json files for each category"""

    city = 'sanfrancsico'

    for cat_num, cat_name in categories.items():
        url = "https://www.eventbriteapi.com/v3/events/search/" + \
              f"?location.address={city}" + \
              f"&categories={cat_num}&token={eventbrite_key}"
        response = requests.get(url)
        data = json.loads(response.text)
        events = data['events']
        for event in events:
            event = make_tabular_eb(event, cat_name)
            insert_event(engine, event)


def read_key(fname):
    """reads in secret key from file
    assumes fname is at base of EC2"""
    with open(expanduser("~") + fname, 'r') as f:
        key = f.readline().strip()
    return key


# read in passwords
# do not change #####
rds_key = read_key('/rds_key')
eventbrite_key = read_key('/eventbrite_key')


# connect to DB
engine = psycopg2.connect(
    database="phil_app",
    user="phil",
    password=rds_key,
    host="phil-app-db.cparuupfbjxx.us-west-2.rds.amazonaws.com",
    port='5432'
)

# make events table if table doesn't exit
table_name = 'events'
if not table_exist(engine, table_name):
    make_events(engine)


# wanted event categories
categories = {103: 'Music', 110: 'Food',
              105: 'Performing & Visual Arts', 109: 'Outdoor'}

# insert events data into table
get_events(categories)
