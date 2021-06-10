import csv
import logging
import os
import requests
import shutil
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout


def write_file(filename, fieldnames, mode, array):
    try:
        with open(f"{filename}.csv", encoding='utf-8-sig', mode=mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(array)
    except Exception as e:
        logging.error(e)
        raise

def create_image_folder(dirname):
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)  
    except OSError as e:
        logging.error(e)
        raise

def download_image(url, filename, dirname):
    try:
        response = requests.get(url, stream=True)
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        logging.error(e)
        raise
    else:
        fileextension = url.split('.')[-1]
        try:
            with open(f'{dirname}/{filename}.{fileextension}', 'wb') as img:
                shutil.copyfileobj(response.raw, img)
            del response
        except OSError as e:
            logging.error(e)
            raise



url = 'https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg'

download_image(url, 'test', './imgs')

