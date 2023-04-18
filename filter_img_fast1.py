from multiprocessing import Pool
from functools import partial
import multiprocessing
import pickle
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import requests
import numpy as np


def get_img_link(name, id):
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

    return img_link


def get_img_links(df, img_link_func):
    df['img_link'] = df.apply(lambda x: img_link_func(x['name'], x['id']), axis=1)
    return df


if __name__ == '__main__':
    df = pd.read_csv('filtered_dataset.csv')
    df = df.head(50).drop('ingredients', axis=1)

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(get_img_links, np.array_split(df, 4), img_link_func=get_img_link)
        df = pd.concat(results)

    with open('filtered_more.pickle', 'wb') as f:
        pickle.dump(df, f)

    df.to_csv('recipes_no_ing1.csv', index=False)
