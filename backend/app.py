import json
import os
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from jaccard import jaccard_similarity
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
# import boolean_search
import pickle

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "admin"
MYSQL_PORT = 3306
MYSQL_DATABASE = "recipes"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__, static_folder="frontend-build")
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

_keys = ['name', 'id', 'minutes', 'tags', 'nutrition', 'steps', 'description', 'ingredients']

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this

def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id","title","descr"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

def boolean_search(ingred_lst):
    ingred_postings = []

    if len(ingred_lst) == 0:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT id FROM mytable WHERE id > 0 AND id <= 10000 LIMIT 1000""" 
        data = mysql_engine.query_selector(query_sql)
        
        posting_set = set()
        data = [str(i) for i in data]
        for tup in data:
            tup = tup[1:-2]
            for p in tup.split(','):
                posting_set.add(p.strip())
        ingred_postings.append(posting_set)
    else:
        for ingred in ingred_lst:
            mysql_engine.query_selector(f"""USE recipes""")
            query_sql = f"""SELECT posting FROM inverted_index WHERE ingredient = '{ingred.lower()}' """ 
            data = mysql_engine.query_selector(query_sql)
            
            posting_set = set()
            data = [str(i) for i in data]
            for tup in data:
                tup = tup[3:len(tup)-4]
                for p in tup.split(','):
                    posting_set.add(p.strip())

            ingred_postings.append(posting_set)

    # print(ingred_postings)
    #perform boolean and on all postings
    result_postings = ingred_postings[0]
    # print(result_postings)
    for i in range(1, len(ingred_postings)):
        curr = ingred_postings[i]
        result_postings = curr.intersection(result_postings)
    # print(result_postings)

    result = []

    for p in result_postings:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT name, id, minutes, tags, nutrition, steps, description, ingredients FROM mytable WHERE id = '{p}' """ 
        data = mysql_engine.query_selector(query_sql)
        for j, val in enumerate(data):
            if j == 4:
                print(val)
                print(type(val))
            values = []
            for i in val:
                if type(i) == str and len(i) > 0 and i[0] == '[':
                    curVal = i.strip('][').replace("'","").split(', ')
                    try:
                        values.append(int(curVal))
                    except Exception:
                        values.append(curVal)
                else:
                    values.append(i)
            
            result.append(dict(zip(_keys, values)))


    return result

def subset_search(ingred_lst):
    mysql_engine.query_selector(f"""USE recipes""")
    if len(ingred_lst) == 1:
        query_sql = f"""SELECT ingredient from inverted_index WHERE ingredient NOT IN ('{ingred_lst[0]}')"""
    else:
        query_sql = f"""SELECT ingredient from inverted_index WHERE ingredient NOT IN {repr(tuple(map(str, ingred_lst)))}"""

    print(query_sql)
    data = mysql_engine.query_selector(query_sql)
    data = [str(i) for i in data][1:-1]
    not_ingred_lst = []

    for tup in data:
        print(tup)
        tup = tup[2:len(tup)-3]
        for p in tup.split(','):
            not_ingred_lst.append(p.strip())
    all_posting_set = set()

    print(not_ingred_lst)

    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""SELECT posting FROM inverted_index""" 
    data = mysql_engine.query_selector(query_sql)
    data = [str(i) for i in data][1:-1]
    
    for tup in data:
        tup = tup[3:-4]
        for p in tup.split(','):
            all_posting_set.add(p.strip())
    
    not_ingred_postings = set()

    for ingred in not_ingred_lst:
        mysql_engine.query_selector(f"""USE recipes""")
        ingred_new = ingred.lower().replace("'","\\\'")
        query_sql = f"""SELECT posting FROM inverted_index WHERE ingredient = '{ingred_new}' """ 
        data = mysql_engine.query_selector(query_sql)
        
        data = [str(i) for i in data]
        for tup in data:
            tup = tup[3:-3]
            for p in tup.split(','):
                not_ingred_postings.add(p.strip())

    diff = all_posting_set.difference(not_ingred_postings)

    result = []
    
    
    for p in diff:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT name, id, minutes, tags, nutrition, steps, description, ingredients FROM mytable WHERE id = '{p}' """ 
        data = mysql_engine.query_selector(query_sql)
        for i in data:
            result.append(dict(zip(_keys,i)))

    return result

def sql_recipe_search(ingred_lst_str):
    ingred_lst = []
    for ingred in ingred_lst_str.split(','):
        ingred_lst.append(ingred.strip())
    
    recipes = boolean_search(ingred_lst, [])

    return json.dumps(recipes)


@app.route("/")
def home():
    # return render_template('base.html',title="sample html")
    return send_from_directory(app.static_folder, "index.html")

# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_search(text)


# @app.route("/recipes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_recipe_search(text)

@app.route("/recipes", methods=['POST'])
def recipes_search():
    body = request.json
    query = body['query']  # string - this is the freeform query
    pantry = body['pantry']  # string list - this is the list of ingredients
    print(query)
    print(pantry)
    # Output is a list of dicts on information about each recipe (jsonified)
    
    # subsets = boolean_search(pantry)
    
    subsets = subset_search(pantry)
    
    print(len(subsets))
    
    descriptions = [str(recipe['name']) + str(recipe['description']) + str(recipe['steps']) for recipe in subsets]

    indices = jaccard_similarity(descriptions, query)

    ranked = [subsets[i] for i in indices][1:9]
    print(len(ranked))
    return json.dumps(ranked)

@app.route("/recipes/<int:id>")
def recipes(id):
    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""SELECT name, id, minutes, tags, nutrition, steps, description, ingredients FROM mytable WHERE id = '{id}' """ 
    data = mysql_engine.query_selector(query_sql)
    return dict(zip(_keys,data[0]))

# app.run(debug=True)