# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:06 2020

@author: OHyic

"""
# Import libraries
import os
import csv
import re
import traceback
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from patch import webdriver_executable


def worker_thread(data):
    (line_count, id, search_key) = data
    try:
        image_scraper = GoogleImageScraper(
            webdriver_path,
            image_path,
            search_key,
            number_of_images,
            headless,
            min_resolution,
            max_resolution,
            max_missed,
        )
    except Exception as e:
        traceback.print_exc()
    image_urls = image_scraper.find_image_urls()
    if len(image_urls) > 0:
        written = False
        while not written:
            with open("result.txt", "a", encoding="utf8") as f:
                f.write(f"{id}, {image_urls[0]}\n")
                written = True
        print(
            f"{line_count} out of {len(search_keys)} which is {line_count/len(search_keys)}%"
        )
    # image_scraper.save_images(image_urls, keep_filenames)

    # Release resources
    del image_scraper


if __name__ == "__main__":
    # Define file path
    webdriver_path = os.path.normpath(
        os.path.join(os.getcwd(), "webdriver", webdriver_executable())
    )
    image_path = os.path.normpath(os.path.join(os.getcwd(), "photos"))

    search_keys = []

    seen_ids = []
    with open("result.txt") as results:
        csv_reader = csv.DictReader(results)
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                seen_ids.append(row["id"])
            line_count += 1

    with open("recipes_no_ing.csv", encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                if row["id"] not in seen_ids:
                    search_keys.append(
                        (line_count, row["id"], re.sub(" +", " ", row["name"]))
                    )
            line_count += 1

    print("done")

    # Parameters
    number_of_images = 1  # Desired number of images
    headless = False  # True = No Chrome GUI
    min_resolution = (500, 500)  # Minimum desired image resolution
    max_resolution = (9999, 9999)  # Maximum desired image resolution
    max_missed = 2  # Max number of failed images before exit
    number_of_workers = 1  # Number of "workers" used
    keep_filenames = False  # Keep original URL image filenames

    # Run each search_key in a separate thread
    # Automatically waits for all threads to finish
    # Removes duplicate strings from search_keys
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=number_of_workers
    ) as executor:
        executor.map(worker_thread, search_keys)
