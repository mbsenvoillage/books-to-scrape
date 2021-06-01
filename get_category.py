from urllib import error
from urllib.parse import urlparse
import logging
from utils import get_page_html
from urllib.error import URLError

url= 'http://books.toscrape.com/catalogue/'

def get_list_of_categories(parsed_html: object):
    ul = parsed_html.find('ul', {'class': 'nav'})
    return ul

def get_all_books_url(parsed_html: object):
    books_container = parsed_html.find('ol', {'class', 'row'})
    h3 = books_container.findAll('h3')
    list_of_url = []
    for el in h3:
        book_url = el.a['href'].replace('../../../', url)
        sanitized_url = urlparse(book_url).geturl()
        list_of_url.append(sanitized_url)
    return list_of_url
