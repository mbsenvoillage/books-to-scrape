import asyncio
from asyncio.tasks import gather
from typing import List
import get_book
import get_category
import utils
import logging
import file_writer
import time


def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()


start = time.time()

async def produce_books(urlQueue: asyncio.Queue, bookQueue: asyncio.Queue, imageUrlQueue: asyncio.Queue):
    url = await urlQueue.get()
    await get_book.scrape(url, bookQueue, imageUrlQueue)
    urlQueue.task_done()

async def consume_books(bookQueue: asyncio.Queue):
    book = await bookQueue.get()
    await file_writer.write_file('books', 'a+', book)
    bookQueue.task_done()
    print(f"consuming books. The size of the queue is: {bookQueue.qsize()}")

async def consume_image_urls(imageUrlQueue: asyncio.Queue):
    image_object = await imageUrlQueue.get()
    await file_writer.download_image(image_object['url'], image_object['filename'])
    imageUrlQueue.task_done()
    print(f"consuming images. The size of the queue is: {imageUrlQueue.qsize()}")


async def main():
    file_writer.write_csv_header('books', 'w')
    bookQueue = asyncio.Queue()
    urlQueue = asyncio.Queue()
    imageQueue = asyncio.Queue()
    try:
        tasks = []
        await gather(get_category.scrape(get_category.cat_with_many_pages, urlQueue), return_exceptions=True)
        tasks.extend(asyncio.create_task(produce_books(urlQueue, bookQueue, imageQueue))for _ in range(2000))
        tasks.extend(asyncio.create_task(consume_books(bookQueue)) for _ in range(2000)) 
        tasks.extend(asyncio.create_task(consume_image_urls(imageQueue)) for _ in range(2000)) 
        await urlQueue.join()  
        await bookQueue.join() 
        await imageQueue.join()  
        for task in tasks:
            task.cancel()   
        await gather(*tasks, return_exceptions=True)
    except Exception as e:
        logging.error(e)
        print("An error occurred")
    else:
        print("Scraping done")


asyncio.run(main())

print(f"took {time.time() - start} seconds")

'File:///Users/yvonmomboisse/Documents/Python/books-to-scrape/imgs/1774749f2cee292f.jpg'