import pandas as pd
import csv
import pickle

# create inverted index of ingredients
def create_inv_idx():
    inv_idx = {}
    df = pd.read_csv('filtered_dataset.csv')

    for index, ingred_lst in enumerate(df['ingredients']):
        recipe_id = int(df['id'][index])
        
        for ingred_unformat in ingred_lst[1:len(ingred_lst)-1].split(','):
            ingred = ingred_unformat.strip()
            ingred = ingred[1:len(ingred)-1]

            if ingred in inv_idx.keys():
                inv_idx[ingred].append(recipe_id)
            else:
                inv_idx.update({ingred:[recipe_id]})
    
    # # to use in boolean not search
    # inv_idx.update({'all recipe ids': []})
    # for id in df['id']:
    #     inv_idx['all recipe ids'].append(id)
    # too long

    for key in inv_idx.keys():
        inv_idx[key].sort()

    return inv_idx

inv_idx = create_inv_idx()

# save the inverted index as a pickle file
with open('ingredients_inverted_index.pickle', 'wb') as f:
    pickle.dump(inv_idx, f)

# save the inverted index as a csv file
w = csv.writer(open("ingredients_inverted_index.csv", "w"))
w.writerow(['ingredients', 'posting'])
for key, val in create_inv_idx().items():
    w.writerow([key, val])


