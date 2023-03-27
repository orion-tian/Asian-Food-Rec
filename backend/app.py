import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
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
MYSQL_USER_PASSWORD = ""
MYSQL_PORT = 3306
MYSQL_DATABASE = "recipes"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id","title","descr"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

def boolean_search(ingred_lst, query_lst):
    ingred_postings = []
    for ingred in ingred_lst:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT posting FROM inverted_index WHERE ingredient = '{ingred.lower()}' """ 
        data = mysql_engine.query_selector(query_sql)
        
        posting_set = set()
        data = [str(i) for i in data]
        for tuple in data:
            tuple = tuple[3:len(tuple)-4]
            for p in tuple.split(','):
                posting_set.add(p.strip())

        ingred_postings.append(posting_set)

        # print(ingred_postings)

    #perform boolean and on all postings
    result_postings = ingred_postings[0]
    for i in range(1, len(ingred_postings)):
        curr = ingred_postings[i]
        result_postings = curr.intersection(result_postings)
    # print(result_postings)

    result = []
    keys = ['name', 'minutes', 'tags', 'nutrition', 'steps', 'description', 'ingredients']
    
    for p in result_postings:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT name, minutes, tags, nutrition, steps, description, ingredients FROM mytable WHERE id = '{p}' """ 
        data = mysql_engine.query_selector(query_sql)
        for i in data:
            result.append(dict(zip(keys,i)))

    return result

def sql_recipe_search(ingred_lst_str):
    ingred_lst = []
    for ingred in ingred_lst_str.split(','):
        ingred_lst.append(ingred.strip())
    
    recipes = boolean_search(ingred_lst, [])

    return json.dumps(recipes)


@app.route("/")
def home():
    return render_template('base.html',title="sample html")

# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_search(text)


# @app.route("/recipes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_recipe_search(text)

@app.route("/recipes", methods=['GET'])
def recipes_search():
    body = request.json
    query = body['query']  # string - this is the freeform query
    pantry = body['pantry']  # string list - this is the list of ingredients

    # Output is a list of dicts on information about each recipe (jsonified)
    return json.dumps(boolean_search(pantry, query))

app.run(debug=True)