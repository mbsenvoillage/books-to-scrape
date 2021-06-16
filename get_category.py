from typing import List
from urllib.parse import urlparse
import logging

from requests.api import get
from utils import get_soup, scrape_item_from_page
import re
import time
import asyncio

baseurl = 'http://books.toscrape.com/catalogue/'
urlwithnext= 'http://books.toscrape.com/catalogue/category/books/childrens_11/index.html'
urlwithoutnext = 'http://books.toscrape.com/catalogue/category/books/self-help_41/index.html'
cat_with_many_pages = 'http://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'

def get_page_book_list(parsed_html: object):
    return parsed_html.find('ol', {'class', 'row'})

def get_next_page_url(parsed_html: object, url: str): 
    return re.sub('[a-z]*.html', parsed_html['href'], url)


def get_link(arr):
    array = []
    for el in arr:
        array.append(el['href'].replace('../../../', baseurl))
    return array

#print(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))

def next_page_url(url, arr: List, starturl):
    arr.append(url)
    soup = get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, starturl))
    if next_url == 'Nothing found':
        return arr
    return next_page_url(next_url, arr, starturl)

def scrape(url: str):  
    category_page_urls = next_page_url(url, [], url)
    list_of_url = []
    for url in category_page_urls:
        soup = get_soup(url)
        list_of_url.extend(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))
    return list_of_url

start = time.time()

print(scrape(cat_with_many_pages))

print(f"took {time.time() - start} seconds")
