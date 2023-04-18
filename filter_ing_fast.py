import csv
import multiprocessing
import requests
import re
from bs4 import BeautifulSoup
import pickle
import pandas as pd
from multiprocessing import Pool

i = 0

def get_img_link(row):
    global i
    name, id = row['name'], row['id']
    kebab_name = re.sub("\s+", "-", name)
    gallery_page = f"https://www.food.com/recipe/{kebab_name}-{id}"

    try:
        html_page = requests.get(gallery_page)
        soup = BeautifulSoup(html_page.text, "html.parser")
        divs = soup.find_all('div', attrs={'class': 'primary-image'})
        img = divs[0].find('img')
        img_link = img['src']
    except:
        img_link = "https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_860,ar_3:2/v1/gk-static/gk/img/recipe-default-images/image-00.svg"

    i += 1
    if i % 50 <= 10:
        print(f"Processed {i} requests")
    
    return img_link


if __name__ == '__main__':
    df = pd.read_csv('filtered_dataset.csv')
    df = df.drop('ingredients', axis=1)
    multiprocessing.set_start_method('fork')

    with Pool(processes=10) as pool:
        df['img_link'] = pool.map(get_img_link, df.to_dict('records'))

    # save the filtered dataset as a pickle file
    with open('filtered_more.pickle', 'wb') as f:
        pickle.dump(df, f)

    df.to_csv('recipes_fast_2.csv', index=False)
