# file no longer needed
import pandas as pd
import pickle

# read the CSV file
df = pd.read_csv('filtered_dataset.csv')

# # get rid of unnecessary columns for now
# # name,id,minutes,contributor_id,submitted,tags,nutrition,n_steps,steps,description,ingredients,n_ingredients
df = df[:500]
# df = df.drop('id', axis=1)
# df = df.drop('minutes', axis=1)
# df = df.drop('contributor_id', axis=1)
# df = df.drop('submitted', axis=1)
# # df = df.drop('tags', axis=1)
# df = df.drop('nutrition', axis=1)
# df = df.drop('n_steps', axis=1)
# df = df.drop('steps', axis=1)
# df = df.drop('description', axis=1)
# df = df.drop('n_ingredients', axis=1)
# df = df[:500]

# save the filtered dataset as a pickle file
with open('filtered_more.pickle', 'wb') as f:
    pickle.dump(df, f)


df.to_csv('filtered_more.csv', index=False)
print(len(df))