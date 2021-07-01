import csv
import logging
import os
import time
from utils import fieldnames
import aiohttp
import aiofiles


async def write_file(filename, mode, book):
    """Writes book info to csv file"""
    try:
        with open(f"{filename}.csv", encoding='utf-8-sig', mode=mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if csv_file.tell() == 0:
                writer.writeheader()
            writer.writerow(book)
    except Exception as e:
        logging.error(e)
        raise

def create_folder(dirname):
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)  
    except OSError as e:
        logging.error(e)
        raise

async def download_image(url, filename, subfolder, dirname='imgs'):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status == 200:
                    create_folder(dirname + '/' + subfolder)
                    fileextension = url.split('.')[-1]
                    async with aiofiles.open(f'{dirname}/{subfolder}/{filename}.{fileextension}', 'wb') as img:
                        await img.write(await res.read())
    except Exception as e:
        logging.error(e)
        logging.error(f"something is wrong with url {url}")
        raise

def get_imgs_dir_path(dirname='imgs') -> str:
    """Takes a directory name and returns the absolute path of that directory"""
    try:
        return os.path.abspath(dirname)
    except OSError as e:
        logging.error(e)
        raise
