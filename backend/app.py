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

_keys = ['name', 'id', 'minutes', 'tags', 'nutrition', 'steps', 'description', 'ingredients', 'img_link']
_keys_user_data = ['recipe_id', 'rating', 'review']

def get_postings_from_data(data):
    return set(row["id"] for row in data)

def get_sql_tuple_from_postings(postings):
    return "(" + str(postings)[1:-1] + ")"

def get_sql_tuple_from_ingredients(ingredient_lst):
    return "(" + str(ingredient_lst)[1:-1].replace("%", "%%") + ")"

def get_user_data_from_postings(result_postings):
   if len(result_postings) == 0:
       return []
   postings_str = get_sql_tuple_from_postings(result_postings)
   mysql_engine.query_selector(f"""USE recipes""")
   query_sql = f"""SELECT recipe_id, rating, review FROM user_data WHERE recipe_id IN {postings_str}"""
  
   data = mysql_engine.query_selector(query_sql)
  
   intermedi = []
   for row in data:
       values = []
       for key in _keys_user_data:
           try:
               values.append(ast.literal_eval(str(row[key])))
           except:
               values.append(row[key])
       intermedi.append(dict(zip(_keys_user_data, values)))
   intermedi = intermedi[1:]

   # combine user data of same recipe together into
   # [{recipe_id:x, user_data:[{rating:x, review:x}, {}]}, {},...]
   results = []
   for d in intermedi:
       recipe_id = d['recipe_id']
       found = False
       for r_d in results:
           if recipe_id == r_d['recipe_id']:
               r_d['user_data'].append({'rating': d['rating'], 'review': d['review']})
               found = True
               break
       if not found:
           results.append({'recipe_id': recipe_id, 'user_data': [{'rating': d['rating'], 'review': d['review']}]})

   return results

def get_recipes_from_postings(result_postings):
    if len(result_postings) == 0:
        return []
    postings_str = get_sql_tuple_from_postings(result_postings)
    mysql_engine.query_selector(f"""USE recipes""")
    query_sql = f"""WITH ings AS (
                        SELECT inverted_index.id, CONCAT("[", group_concat(QUOTE(inverted_index.ingredient)), "]") AS ingredients 
                        FROM inverted_index GROUP BY inverted_index.id
                    )
                    SELECT name, mytable.id, minutes, tags, nutrition, steps, description, ings.ingredients, img_link
                    FROM mytable 
                    INNER JOIN ings
                    ON mytable.id = ings.id
                    WHERE mytable.id IN {postings_str}""" 
    
    data = mysql_engine.query_selector(query_sql)
    
    results = []
    for row in data:
        values = []
        for key in _keys:
            try:
                values.append(ast.literal_eval(str(row[key])))
            except:
                values.append(row[key])
        results.append(dict(zip(_keys, values)))
    return results[1:]

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
    if len(ingred_lst) == 0:
        return boolean_search(ingred_lst)
    if len(ingred_lst) == 1:
        query_sql = f"""SELECT DISTINCT ingredient from inverted_index WHERE ingredient NOT IN ('{ingred_lst[0]}')"""
    else:
        query_sql = f"""SELECT DISTINCT ingredient from inverted_index WHERE ingredient NOT IN {repr(tuple(map(str, ingred_lst)))}"""

    data = mysql_engine.query_selector(query_sql)
    not_ingred_lst = [row["ingredient"] for row in data]

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

    # Output is a list of dicts on information about each recipe (jsonified)
    
    # subsets = boolean_search(pantry)

    subsets = subset_search(pantry)
    
    descriptions = [str(recipe['name']) + str(recipe['description']) + str(recipe['steps']) for recipe in subsets]

    indices = jaccard_similarity(descriptions, query)

    ranked = [subsets[i] for i in indices][0:9]

    return json.dumps(ranked)

@app.route("/recipes/<int:id>")
def recipes(id):
    recipe = get_recipes_from_postings([0, id])
    if len(recipe) == 1:
        return json.dumps(recipe[0])
    else:
        return json.dumps({})

# app.run(debug=True)