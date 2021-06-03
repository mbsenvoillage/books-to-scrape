import get_book
import urllib
import get_category
import utils
import logging



url = 'http://books.toscrape.com/'

infos = [
"product_page_url",
"universal_product_code (upc)",
"title",
"price_including_tax",
"price_excluding_tax",
"number_available",
"product_description",
"category",
"review_rating",
"image_url",
]

def init_logger():
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    init_logger()

try:
    all_books_from_category = []
    cat_page_urls = get_category.scrape(get_category.urlwithoutnext)
    for arrayofurls in cat_page_urls:
        for url in arrayofurls:
            all_books_from_category.append(get_book.scrape(url))
except Exception as e:
    print(e)
else:
    print(all_books_from_category)

# try:
#     urllib.request.urlretrieve('http://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg', './pic.jpg')
# except Exception as e:
#     print(e)

