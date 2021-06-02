import get_book
import get_category
import utils
from pymongo import MongoClient
import time
import concurrent.futures

client = MongoClient()
mydb = client["mydatabase"]
mycol = mydb["books"]

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

def title_push(url):
    title = get_book.scrape(url)['title']    
    mydict = { "url": url, "title": title }
    x = mycol.insert_one(mydict)

list_of_books = get_category.get_all_books_url(utils.get_page_html('http://books.toscrape.com/catalogue/category/books/classics_6/index.html'))

startTime = time.time()
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for url in list_of_books:
        futures.append(executor.submit(title_push, url=url))

executionTime = (time.time() - startTime)

print('Execution time in seconds: ' + str(executionTime))
print(f'len of books: {len(list_of_books)}')

for x in mycol.find():
    print(x)
