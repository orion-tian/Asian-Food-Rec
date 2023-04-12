# file no longer needed
import pandas as pd
import pickle

# read the CSV file
df = pd.read_csv('filtered_dataset.csv')
df = df.drop('ingredients', axis=1)
# save the filtered dataset as a pickle file
with open('filtered_more.pickle', 'wb') as f:
    pickle.dump(df, f)

df.to_csv('recipes_no_ing.csv', index=False)
