import csv
import requests
import re
from bs4 import BeautifulSoup
import pickle
import pandas as pd

i = 0


def get_img_link(name, id):
    global i
    kebab_name = re.sub("\s+", "-", name)
    gallery_page = f"https://www.food.com/recipe/{kebab_name}-{id}"

    try:
        # print(gallery_page)
        html_page = requests.get(gallery_page)
        soup = BeautifulSoup(html_page.text, "html.parser")
        divs = soup.find_all('div', attrs={'class': 'primary-image'})
        img = divs[0].find('img')
        img_link = img['src']
    except:
        img_link = "https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_860,ar_3:2/v1/gk-static/gk/img/recipe-default-images/image-00.svg"
    i += 1
    if i % 100 == 0:
        print(i)

    return img_link

df = pd.read_csv('recipes_fast.csv')
print(df.shape[0])
# df = df.drop('ingredients', axis=1)

# df['img_link'] = df.apply(lambda x: get_img_link(x['name'], x['id']), axis=1)

# # save the filtered dataset as a pickle file
# with open('filtered_more.pickle', 'wb') as f:
#     pickle.dump(df, f)

# df.to_csv('recipes_no_ing1.csv', index=False)





# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/90/92/1/picObZtgm.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/37/84/1/picz5yATQ.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/66/93/2/vEx2xP3QR4aZLGqUAjQ7_DSC04908-2.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/12/02/97/picLsVzrq.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/30/54/31/picjYcXGC.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/41/87/56/pics6jfVu.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/feed/481195/tTMfKy4XRQeAFo2KpX5E_IMG_20170917_205849_446.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/97/96/8/piczv3sA0.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/32/56/57/pickksRFJ.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/53/11/43/Vdi99aJT9KE7Q0fGHSfi_0S9A9533.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/44/85/08/picXaYazO.jpg
# # https://img.sndimg.com/food/image/upload/f_auto,c_thumb,q_55,w_250,ar_5:4/v1/img/recipes/66/80/0/picGIqUJ2.jpg