import asyncio
from asyncio.tasks import gather
from typing import List
import get_book
import get_category
import utils
import logging
import file_writer
import time
import sys

base = 'http://books.toscrape.com/'


def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()

args = sys.argv[1:]

url = ''

if (len(args) > 1):
    print("This program only takes zero or one argument")
    exit()
elif (len(args) == 0):
    url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
else:
    if (args[0] == 'http://books.toscrape.com/'):
        url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    else:
        url = args[0]



start = time.time()

async def produce_books(urlQueue: asyncio.Queue, bookQueue: asyncio.Queue, imageUrlQueue: asyncio.Queue):
    url = await urlQueue.get()
    await get_book.scrape(url, bookQueue, imageUrlQueue)
    urlQueue.task_done()

async def consume_books(bookQueue: asyncio.Queue):
    book = await bookQueue.get()
    await file_writer.write_file('books', 'a+', book)
    bookQueue.task_done()

async def consume_image_urls(imageUrlQueue: asyncio.Queue, img_subfolfer):
    image_object = await imageUrlQueue.get()
    await file_writer.download_image(image_object['url'], image_object['filename'], img_subfolfer)
    imageUrlQueue.task_done()


async def main(url):
    file_writer.write_csv_header('books', 'w')
    bookQueue = asyncio.Queue()
    urlQueue = asyncio.Queue()
    imageQueue = asyncio.Queue()
    img_subfolder = '_'.join(time.ctime().split())
    try:
        tasks = []
        await gather(get_category.scrape(url, urlQueue, 1000), return_exceptions=True)
        tasks.extend(asyncio.create_task(produce_books(urlQueue, bookQueue, imageQueue))for _ in range(2000))
        tasks.extend(asyncio.create_task(consume_books(bookQueue)) for _ in range(2000))   
        tasks.extend(asyncio.create_task(consume_image_urls(imageQueue, img_subfolder)) for _ in range(2000))   
        await urlQueue.join()  
        await bookQueue.join()
        await imageQueue.join()  
        for task in tasks:
            task.cancel()   
        await gather(*tasks, return_exceptions=True)
    except Exception as e:
        logging.error(e)
        print("An error occurred")
        exit()
    else:
        print("Scraping done")


asyncio.run(main(url))

print(f"took {time.time() - start} seconds")
