# file no longer needed
import pandas as pd
import pickle

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time

# read the CSV file
df = pd.read_csv('filtered_dataset.csv')
df = df.drop('ingredients', axis=1)
i = 0
def get_img_link(name, id):
    global i
    kebab_name = re.sub("\s+", "-", name)

    gallery_page = f"""https://food.com/recipe/{kebab_name}-{id}#gallery"""

    done = False
    while (not done):
        try:
            html_page = urlopen(gallery_page)
            soup = BeautifulSoup(html_page, "html5lib")
            done = True
        except ConnectionResetError:
            done = False
            time.sleep(10)

    i += 1
    if i % 100 == 0:
        print(i)
    return soup.find('img').get('src')

df['img_link'] = df.apply(lambda x: get_img_link(x['name'], x['id']), axis=1)

# save the filtered dataset as a pickle file
with open('filtered_more.pickle', 'wb') as f:
    pickle.dump(df, f)

df.to_csv('recipes_no_ing.csv', index=False)
