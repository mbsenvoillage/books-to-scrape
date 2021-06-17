import get_book
import get_category
import utils
import logging
import file_writer
import asyncio


def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()

async def scrape(bookQueue):
    urlQueue = asyncio.Queue()  
    try:
        producers = [asyncio.create_task(get_category.scrape(get_category.urlwithnext, urlQueue))]
        consumers = [asyncio.create_task(get_book.scrape(urlQueue, bookQueue))]
        await asyncio.gather(*producers)
        await urlQueue.join()
        for c in consumers:
            c.cancel()
        # for book_url in books_urls:
        #     all_books_from_category.append(get_book.scrape(book_url))
        # file_writer.write_file('books', 'w+', all_books_from_category)
    except Exception as e:
        logging.error(e)
        print("An error occurred")

async def write(queue):
    while True:
        item = await queue.get()
        if item is None:
            pass
        # file_writer.write_file('books', 'w+', item)
        print(item)
        queue.task_done()

async def main():
    bookQueue = asyncio.Queue()
    try:
        # producers = [asyncio.create_task(scrape(bookQueue))]
        await scrape(bookQueue)
        # consumers = [asyncio.create_task(write(bookQueue))]
        # await asyncio.gather(*producers)
        # await bookQueue.join()
        # for c in consumers:
        #     c.cancel()
    except Exception as e:
        print(e)
    else:
        print("scraping done")

asyncio.run(main())


'File:///Users/yvonmomboisse/Documents/Python/books-to-scrape/imgs/1774749f2cee292f.jpg'