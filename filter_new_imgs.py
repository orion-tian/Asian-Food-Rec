import pandas as pd
import pickle


df_imgs = pd.read_csv('result copy.txt', sep=', ', header=0)
df_recipes = pd.read_csv('recipes_fast_3.csv')

for index, row in df_imgs.iterrows():
  index = df_recipes.index[df_recipes['id'] == row['id']]
  df_recipes.at[index,'img_link']=row['img_url9999']

df_recipes.to_csv('recipes_fast_4.csv', index=False)



