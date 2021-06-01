import get_book
import urllib
import get_category
import utils


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

try:
    list_of_books = get_category.get_all_books_url(utils.get_page_html('http://books.toscrape.com/catalogue/category/books/classics_6/index.html'))
    books_dets = []
    for url in list_of_books:
        print(get_book.scrape(url)['title'])
except Exception as e:
    print(e)
else:
    print(books_dets)

# try:
#     urllib.request.urlretrieve('http://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg', './pic.jpg')
# except Exception as e:
#     print(e)

