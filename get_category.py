from urllib.parse import urlparse
import logging
from utils import get_page_html, is_page_scrapable
import re
import utils

baseurl = 'http://books.toscrape.com/catalogue/'
urlwithnext= 'http://books.toscrape.com/catalogue/category/books/childrens_11/index.html'
urlwithoutnext = 'http://books.toscrape.com/catalogue/category/books/self-help_41/index.html'

def get_list_of_categories(parsed_html: object):
    ul = parsed_html.find('ul', {'class': 'nav'})
    return ul

def get_page_book_list(parsed_html: object):
    return parsed_html.find('ol', {'class', 'row'})

def go_to_next_page(parsed_html: object, url: str):
    next_page_url = ''
    href = ''
    try:
        next = parsed_html.find('li', {'class', 'next'})
        href = next.a['href']
    except Exception as e:
        logging.error(e)
    else:
        next_page_url = re.sub('[a-z]*.html', href, url)
    return next_page_url

def test():
    print(go_to_next_page(utils.get_page_html(urlwithnext), urlwithnext))

def get_all_books_url(parsed_html: object):
    books_container = get_page_book_list(parsed_html)
    list_of_url = []
    try:
        h3 = books_container.findAll('h3')
    except Exception as e:
        logging.error(e)
    else:
        for el in h3:
            try:
                book_url = el.a['href'].replace('../../../', baseurl)
                assert book_url != None, "Could not retrieve the book's URL"
            except AssertionError as e:
                logging.info(e)
            else:  
                sanitized_url = urlparse(book_url).geturl()
                list_of_url.append(sanitized_url)
    return list_of_url

def scrape(url: str):
    html = is_page_scrapable(url)
    list_of_url = []
    list_of_url.append(get_all_books_url(html))
    #print(list_of_url)s
    next = go_to_next_page(html, url)
    while next != None:
        html = is_page_scrapable(urlparse(next).geturl())
        list_of_url.append(get_all_books_url(html))
        next = go_to_next_page(html, url)
    return list_of_url
