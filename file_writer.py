import asyncio
import csv
import logging
import os
import requests
import shutil
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout
from utils import fieldnames


def write_file(filename, mode, book):
    try:
        with open(f"{filename}.csv", encoding='utf-8-sig', mode=mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(book)
    except Exception as e:
        logging.error(e)
        raise

def write_csv_header(filename, mode):
    try:
        with open(f"{filename}.csv", encoding='utf-8-sig', mode=mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
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

def download_image(url, filename, dirname='imgs'):
    try:
        response = requests.get(url, stream=True)
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        logging.error(e)
        raise
    else:
        fileextension = url.split('.')[-1]
        try:
            create_image_folder(dirname)
            with open(f'{dirname}/{filename}.{fileextension}', 'wb') as img:
                shutil.copyfileobj(response.raw, img)
            del response
        except OSError as e:
            logging.error(e)
            raise

def get_imgs_dir_path(dirname='imgs') -> str:
    try:
        return os.path.abspath(dirname)
    except OSError as e:
        logging.error(e)
        raise


url = 'https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg'

# download_image(url, 'test', 'imgs')
