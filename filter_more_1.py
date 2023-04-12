import pandas as pd

# Read the input CSV file into a pandas DataFrame
df = pd.read_csv('filtered_dataset.csv')

# Split the ingredients column into a list of strings and explode it
df['ingredients'] = df['ingredients'].str.strip('[]').str.split(', ')
df = df.explode('ingredients')

# Rename the columns of the output DataFrame
ingredient_recipe_df = df.rename(columns={'ingredients': 'Ingredient', 'id': 'id'})[['Ingredient', 'id']]

# Write the output CSV file
ingredient_recipe_df.to_csv('ingredients.csv', index=False)
