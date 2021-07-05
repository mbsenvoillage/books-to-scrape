import asyncio
from asyncio.tasks import gather
import re
import get_book
import get_category
import logging
import file_writer
import time
import sys

def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'

start = time.time()

async def produce_books(url_queue: asyncio.Queue, book_queue: asyncio.Queue, imageurl_queue: asyncio.Queue):
    """Gets book page url off the url_queue and scrapes the book page"""
    url = await url_queue.get()
    await get_book.scrape(url, book_queue, imageurl_queue)
    url_queue.task_done()

async def consume_books(book_queue: asyncio.Queue):
    """Gets book dict off the book_queue and writes the book info to csv"""
    book = await book_queue.get()
    cat = book['category']
    await file_writer.write_file(f'./csv/{cat}', 'a', book)
    book_queue.task_done()

async def consume_image_urls(imageurl_queue: asyncio.Queue, img_subfolfer):
    """Gets image url off a queue and downloads the image"""
    image_object = await imageurl_queue.get()
    await file_writer.download_image(image_object['url'], image_object['filename'], img_subfolfer)
    imageurl_queue.task_done()


async def main(url):
    file_writer.create_folder('csv')    
    book_queue = asyncio.Queue()
    url_queue = asyncio.Queue()
    image_queue = asyncio.Queue()
    img_subfolder = '_'.join(time.ctime().split())
    try:
        tasks = []
        await gather(get_category.scrape(url, url_queue, 1000), return_exceptions=True)
        tasks.extend(asyncio.create_task(produce_books(url_queue, book_queue, image_queue))for _ in range(2000))
        tasks.extend(asyncio.create_task(consume_books(book_queue)) for _ in range(2000))   
        tasks.extend(asyncio.create_task(consume_image_urls(image_queue, img_subfolder)) for _ in range(2000))   
        await url_queue.join()  
        await book_queue.join()
        await image_queue.join()  
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
