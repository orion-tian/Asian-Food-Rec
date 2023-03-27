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
MYSQL_DATABASE = "kardashiandb"

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
    query_sql = f"""SELECT * FROM mytable"""
    data = mysql_engine.query_selector(query_sql)

    result = []
    keys = ["name","id","minutes", "contributor_id", "submitted", "tags", "nutrition", 
                "n_steps", "steps", "description", "ingredients", "n_ingredients"]
    # since I was tyring to do the dumbest way of looking through every row
    # of table and checking if the recipe's ingredients was subset of inputted ingredients
    # then add recipe to result list
    for row in data:
        data_dict = dict(zip(keys,row))
        print(data_dict)
        print()
        # recipe_ingred_lst = []
        # ingred_lst_str = data_dict['ingredients'].strip()
        # ingred_lst_str = ingred_lst_str[1:len(ingred_lst_str)-1]
        # for i in ingred_lst_str.split(','):
        #     ingred = i.strip()
        #     ingred = ingred[1:len(ingred)-1]
        #     # print(ingred)
        #     recipe_ingred_lst.append(ingred)

        # print(recipe_ingred_lst)
        # print()
        # if set(recipe_ingred_lst).issubset(set(ingred_lst)):
        #     result.append((data_dict['name'], data_dict['id'], data_dict['ingredients']))

    # return result
    return []

def sql_recipe_search(ingred_lst_str):
    ingred_lst = []
    for ingred in ingred_lst_str.split(','):
        ingred_lst.append(ingred.strip())
    
    recipe_ids = boolean_search(ingred_lst, [])

    # print(recipe_ids)
   
    # keys = ["name","id","minutes", "contributor_id"]
    # for recipe_id in recipe_ids:
    #     query_sql = f"""SELECT * FROM mytable WHERE id = '%%{recipe_id}%%'"""
    #     data.append(mysql_engine.query_selector(query_sql))
    
    
    query_sql = f"""SELECT * FROM mytable WHERE LOWER( name ) LIKE '%%{ingred_lst_str.lower()}%%' limit 10"""
    # keys = ["name","id","minutes", "contributor_id", "submitted", "tags", "nutrition", 
        #         "n_steps", "steps", "description", "ingredients", "n_ingredients"]
    keys = ["name","id","minutes", "contributor_id"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])


@app.route("/")
def home():
    return render_template('base.html',title="sample html")

# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_search(text)

@app.route("/recipes")
def episodes_search():
    text = request.args.get("title")
    return sql_recipe_search(text)

app.run(debug=True)