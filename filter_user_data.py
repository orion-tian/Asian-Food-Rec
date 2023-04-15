import pandas as pd
import pickle

# read the CSV file
df = pd.read_csv('RAW_interactions.csv')
filtered_dataset = pd.read_csv('filtered_dataset.csv')

# original colums: user_id,recipe_id,date,rating,review
df = df.drop("user_id", axis=1)
df = df.drop("date", axis=1)

lst_of_relv_recip_ids = filtered_dataset['id'].values.tolist()
df = df[df['recipe_id'].isin(lst_of_relv_recip_ids)]

with open('user_data.pickle', 'wb') as f:
  pickle.dump(df, f)

df.to_csv('user_data.csv', index=False)
print(len(df))