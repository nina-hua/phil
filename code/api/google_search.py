import psycopg2  # new package - need to update yml file
import requests
import json
import re
import wikipedia  # new package - need to update yml file
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


def insert_attraction(engine, att):
    """given a database connection and
    a tabular form of a google event,
    insert into the attractions table"""

    with engine.cursor() as cur:
        cmd = """INSERT INTO public.attractions
        (att_name, att_address, att_rating, att_desc, att_category)
        VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(cmd, (att[0], att[1], att[2], att[3], att[4]))
        engine.commit()


def make_attraction(engine):
    """given a database connection,
    create an attraction table"""
    with engine.cursor() as cur:
        make_table = """CREATE TABLE public.attractions
        (ID serial PRIMARY KEY,
         att_name VARCHAR (255),
         att_desc TEXT,
         att_address VARCHAR(225),
         att_rating INT,
         att_category VARCHAR(255));"""
        cur.execute(make_table)
        engine.commit()


def term_search_api(term):
    """Uses Google's Place Search API
    Given a search term, will search for place and
    return information about the place as json"""

    web_term = re.sub(r"\s", "%20", term)
    fields = ["photos", "formatted_address", "name",
              "rating", "geometry", "types", "price_level"]
    web_fields = ','.join(fields)

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/" + \
        "json?" + f"input={web_term}&inputtype=textquery&" + \
        f"fields={web_fields}&key={google_key}"
    response = requests.get(url)
    data = json.loads(response.text)

    return data


def clean_text(text):
    """given a string, remove any tabs"""
    try:
        clean = re.sub('\t', '. ', text)
        clean = re.sub('\n', '. ', clean)
        return clean
    except KeyError:
        return text


def make_tabular_google(result):
    """given a json object from google search api,
    manipulate results into tabular form"""

    # first candiate is what we will use as the event
    attraction = result['candidates'][0]

    att_address = attraction['formatted_address']
    att_name = attraction['name']
    att_category = attraction['category']

    try:
        att_rating = float(attraction['rating'])
    except KeyError:  # no rating
        att_rating = None

    try:
        att_desc = clean_text(attraction['summary'])
    except KeyError:  # no summary
        att_desc = None

    return (att_name, att_address, att_rating, att_desc, att_category)


def get_attractions(attractions):
    """updates data for attraction event"""

    for attraction, att_category in attractions:
        result = term_search_api(attraction)
        result['candidates'][0]['category'] = att_category

        try:  # some attractions don't have wikipedia pages
            result['candidates'][0]['summary'] = wikipedia.summary(attraction)
        except KeyError:
            pass

        result = make_tabular_google(result)
        insert_attraction(engine, result)


def read_key(fname):
    """reads in secret key from file
    assumes fname is at base of EC2"""
    with open(expanduser("~") + fname, 'r') as f:
        key = f.readline().strip()
    return key


# read in db password
# do not change #####
rds_key = read_key('/rds_key')
google_key = read_key('/google_key')

# connect to DB
engine = psycopg2.connect(
    database="phil_app",
    user="phil",
    password=rds_key,
    host="phil-app-db.cparuupfbjxx.us-west-2.rds.amazonaws.com",
    port='5432'
)

# set up attractions table
table_name = 'attractions'
if not table_exist(engine, table_name):  # make table
    make_attraction(engine)
else:  # drop table and make table
    with engine.cursor() as cur:
        drop_table = """DROP TABLE public.attractions;"""
        cur.execute(drop_table)
        engine.commit()
    make_attraction(engine)

# wanted attractions
attractions = [('Pier 39', 'Food & Drink'),
               ('Golden Gate Bridge', 'Landmark'),
               ('Golden Gate Park', 'Travel & Outdoor'),
               ('Lombard Street (San Francisco)', 'Landmark'),
               ('Alcatraz Island', 'Museum'),
               ('California Academy of Sciences', 'Museum'),
               ('The de Young Museum', 'Museum'),
               ('San Francisco Museum of Modern Art', 'Museum'),
               ('Presidio of San Francisco', 'Travel & Outdoor'),
               ('Yerba Buena Gardens', 'Travel & Outdoor'),
               ('The Cable Car Museum', 'Museum'),
               ('Crissy Field', 'Travel & Outdoor'),
               ('Asian Art Museum (San Francisco)', 'Museum'),
               ('The Exploratorium', 'Museum'),
               ('San Francisco Giants at Oracle Park', 'Travel & Outdoor'),
               ('Angel Island State Park', 'Travel & Outdoor'),
               ('Contemporary Jewish Museum', 'Museum'),
               ('San Francisco Symphony', 'Performing & Visual Arts'),
               ('San Francisco Zoo and Gardens', 'Museum'),
               ('Twin Peaks (San Francisco)', 'Travel & Outdoor'),
               ('Palace of Fine Arts', 'Landmark'),
               ("Fisherman's Wharf", 'Food & Drink'),
               ('Union Square, San Francisco', 'Landmark'),
               ('Painted Ladies', 'Landmark'),
               ('Alamo Square', 'Travel & Outdoor'),
               ('Chinatown, San Francisco', 'Landmark'),
               ('Japanese Tea Garden (San Francisco)', 'Museum'),
               ('Coit Tower', 'Landmark'),
               ('Castro District', 'Landmark'),
               ('Ghirardelli Square', 'Landmark'),
               ('Ferry Building', 'Landmark'),
               ('Dolores Park', 'Travel & Outdoor')]

# insert attraction data into table
get_attractions(attractions)
