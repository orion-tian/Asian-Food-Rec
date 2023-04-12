import pandas as pd

df = pd.read_csv('filtered_dataset.csv')
df['ingredients'] = df['ingredients'].str.strip('[]').str.split(', ')
df = df.explode('ingredients')
df['ingredients'] = df['ingredients'].str.strip('\'\"')
df.sort_values(by=['ingredients', 'id'], inplace=True)

ingredient_recipe_df = df.rename(columns={'ingredients': 'Ingredient', 'id': 'id'})[['Ingredient', 'id']]
ingredient_recipe_df.to_csv('ingredients.csv', index=False)
