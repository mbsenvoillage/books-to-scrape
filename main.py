import asyncio
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

async def main():
    queue = asyncio.Queue()
    try:
        all_books_from_category = []
        books_urls = await get_category.scrape(get_category.cat_with_many_pages)
        tasks = [asyncio.create_task(get_book.scrape(book_url, queue)) for book_url in books_urls]
        await asyncio.gather(*tasks)
        # print(all_books_from_category)
        # file_writer.write_file('books', 'w+', all_books_from_category)
    except Exception as e:
        logging.error(e)
        print("An error occurred")
    else:
        print("Scraping done")


asyncio.run(main())

print(f"took {time.time() - start} seconds")

'File:///Users/yvonmomboisse/Documents/Python/books-to-scrape/imgs/1774749f2cee292f.jpg'