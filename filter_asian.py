import pandas as pd
import pickle

# read the CSV file
df = pd.read_csv('RAW_recipes.csv')

# filter the rows based on the "tags" column
df = df[df['tags'].str.contains('asian|chinese|japanese|korean|indian', case=False)]

# save the filtered dataset as a pickle file
with open('filtered_dataset.pickle', 'wb') as f:
    pickle.dump(df, f)


df.to_csv('filtered_dataset.csv', index=False)
print(len(df))