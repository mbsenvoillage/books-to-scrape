import get_book
import get_category
import utils
import logging
import file_writer


def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()

try:
    all_books_from_category = []
    books_urls = get_category.scrape(get_category.urlwithnext)
    for book_url in books_urls:
        all_books_from_category.append(get_book.scrape(book_url))
    file_writer.write_file('books', 'w+', all_books_from_category)
except Exception as e:
    logging.error(e)
    print("An error occurred")
else:
    print("Scraping done")

'File:///Users/yvonmomboisse/Documents/Python/books-to-scrape/imgs/1774749f2cee292f.jpg'