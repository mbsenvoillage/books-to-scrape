import get_book
import urllib


url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

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
    cat = get_book.scrape(url)
except Exception as e:
    print(e)
else:
    print(cat)

# try:
#     urllib.request.urlretrieve('http://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg', './pic.jpg')
# except Exception as e:
#     print(e)
