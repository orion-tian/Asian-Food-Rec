import json
import os
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from jaccard import jaccard_similarity
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
# import boolean_search
import pickle
import ast

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

app = Flask(__name__, static_url_path='',)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# _keys = ['name', 'id', 'minutes', 'tags', 'nutrition', 'steps', 'description', 'ingredients']
_keys_modifed = ['name', 'id', 'minutes', 'nutrition', 'ingredients']

def get_postings_from_data(data):
    data = [str(i) for i in data]

    postings = set()

    for tup in data:
        tup = tup[1:-2]
        postings.add(int(tup))

    return postings

def get_sql_tuple_from_postings(postings):
    return "(" + str(postings)[1:-1] + ")"

def get_sql_tuple_from_ingredients(ingredient_lst):
    return "(" + str(ingredient_lst)[1:-1].replace("%", "%%") + ")"

def get_fields_too_long(field, postings_str):
    len_wo_trun = 250
    magic_num_min_len = 50
    
    postings_lst = [p.strip() for p in postings_str[1:-1].split(',')]
    result = []
    for i in range(len(postings_lst)):
        result.append("")

    # substring doesn't work if one of the strings has index out of bounds 
    # so go one by one
    for i, p in enumerate(postings_lst):
        
        length_of_result = len_wo_trun
        index = 1
        
        while length_of_result >= magic_num_min_len:
            mysql_engine.query_selector(f"""USE recipes""")
            query_sql = f"""
                        SELECT SUBSTRING({field}, {index}, {len_wo_trun})
                        FROM mytable 
                        WHERE mytable.id = {p}""" 
        
            data = mysql_engine.query_selector(query_sql)
            data = [str(i) for i in data]
            tup = ast.literal_eval(data[0])
            for val in tup:
                curVal = val.strip('][').replace("'","")
                result[i] += curVal
                index += len_wo_trun
            length_of_result = len(curVal)
    
    return result

def get_recipes_from_postings(result_postings):
    if len(result_postings) == 0:
        return []
    postings_str = get_sql_tuple_from_postings(result_postings)
    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""WITH ings AS (
                        SELECT inverted_index.id, CONCAT("[", group_concat(inverted_index.ingredient), "]") AS ingredients 
                        FROM inverted_index GROUP BY inverted_index.id
                    )
                    SELECT name, mytable.id, minutes, nutrition, ings.ingredients 
                    FROM mytable 
                    INNER JOIN ings
                    ON mytable.id = ings.id
                    WHERE mytable.id IN {postings_str}""" 
    
    data = mysql_engine.query_selector(query_sql)
    data = [str(i) for i in data]
    result = []
    for recipe in data:
        tup = ast.literal_eval(recipe)
        values = []
        for val in tup:
            if type(val) == str and len(val) > 0 and val[0] == '[':
                curVal = val.strip('][').replace("'","").split(',')
                curVal = [v.strip() for v in curVal]
                try:
                    values.append(int(curVal))
                except Exception:
                    values.append(curVal)
            else:
                values.append(val)
            
        result.append(dict(zip(_keys_modifed, values)))
    
    # get steps field
    steps_lst = get_fields_too_long('steps', postings_str)
    for i, steps in enumerate(steps_lst):
        result[i].update({'steps': steps})

    # get tags field
    tags_lst = get_fields_too_long('tags', postings_str)
    for i, tags in enumerate(tags_lst):
        result[i].update({'tags': [t.strip() for t in tags.split(',')]})

    # get description field
    descrip_lst = get_fields_too_long('description', postings_str)
    for i, descrp in enumerate(descrip_lst):
        result[i].update({'description': descrp})
    
    return result

# returns postings that contain any of the ingredients in ingredients list
def get_postings_containing_ingredients(ingredient_lst):
    ingred_str = get_sql_tuple_from_ingredients(ingredient_lst)

    mysql_engine.query_selector(f"""USE recipes""")

    query_sql = f"""SELECT DISTINCT id FROM inverted_index WHERE ingredient in {ingred_str}""" 
    data = mysql_engine.query_selector(query_sql)
    
    return get_postings_from_data(data)

def get_postings_containing_all_ingredients(ingredient_lst):
    ingred_str = get_sql_tuple_from_ingredients(ingredient_lst)
    length = len(ingredient_lst)

    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""SELECT DISTINCT id FROM inverted_index WHERE ingredient in {ingred_str} GROUP BY id HAVING COUNT(*) = {length}""" 

    data = mysql_engine.query_selector(query_sql)

    return get_postings_from_data(data)

def boolean_search(ingred_lst):
    posting_set = set()
    if len(ingred_lst) == 0:
        mysql_engine.query_selector(f"""USE recipes""")
        query_sql = f"""SELECT id FROM mytable LIMIT 1000""" 
        data = mysql_engine.query_selector(query_sql)
        posting_set = get_postings_from_data(data)
    else:
        posting_set = get_postings_containing_all_ingredients(ingred_lst)

    if len(posting_set) > 0:
        return get_recipes_from_postings(posting_set)
    else:
        return boolean_search([])

def subset_search(ingred_lst):
    mysql_engine.query_selector(f"""USE recipes""")
    print(ingred_lst)
    if len(ingred_lst) == 0:
        return boolean_search(ingred_lst)
    if len(ingred_lst) == 1:
        query_sql = f"""SELECT DISTINCT ingredient from inverted_index WHERE ingredient NOT IN ('{ingred_lst[0]}')"""
    else:
        query_sql = f"""SELECT DISTINCT ingredient from inverted_index WHERE ingredient NOT IN {repr(tuple(map(str, ingred_lst)))}"""

    print(query_sql)
    data = mysql_engine.query_selector(query_sql)
    data = [str(i) for i in data][1:-1]
    not_ingred_lst = []

    for tup in data:
        tup = tup[2:len(tup)-3]
        for p in tup.split(','):
            not_ingred_lst.append(p.strip())
    all_posting_set = set()

    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""SELECT id FROM inverted_index""" 
    data = mysql_engine.query_selector(query_sql)
    
    all_posting_set = get_postings_from_data(data)
    all_posting_set.remove(0)

    not_ingred_postings = get_postings_containing_ingredients(not_ingred_lst)

    diff = all_posting_set.difference(not_ingred_postings)
    
    if len(diff) > 0:
        return get_recipes_from_postings(diff)
    else:
        return boolean_search(ingred_lst)

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

    ranked = [subsets[i] for i in indices][0:9]
    print(len(ranked))
    return json.dumps(ranked)

@app.route("/recipes/<int:id>")
def recipes(id):
    return get_recipes_from_postings([id])

# app.run(debug=True)