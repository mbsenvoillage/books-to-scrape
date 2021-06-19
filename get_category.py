from asyncio.tasks import gather
from os import truncate
from typing import List
from urllib.parse import urlparse
import logging
import math

from requests.api import get
from utils import get_soup, scrape_item_from_page
import re
import time
import asyncio

baseurl = 'http://books.toscrape.com/catalogue/'
urlwithnext= 'http://books.toscrape.com/catalogue/category/books/childrens_11/index.html'
urlwithoutnext = 'http://books.toscrape.com/catalogue/category/books/self-help_41/index.html'
cat_with_some_pages = 'http://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'
cat_with_many_pages = 'http://books.toscrape.com/catalogue/category/books_1/index.html'

def reformat_cat_page_url(url: str, index: int=None, parsed_html: object=None):
    replace_with = parsed_html['href'] if index is None else f'page-{index}.html'
    return re.sub('[a-z]*.html', replace_with, url)
  
def reformat_book_page_urls(arr: List):
    """ Takes an array of shortened URLs from href tags, and returns a new array with full length URL"""
    pattern = '../../../' if '../../../' in arr[0]['href'] else '../../'
    return [el['href'].replace(pattern, baseurl) for el in arr]

async def cat_page_url(url, starturl, stock):
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: reformat_cat_page_url(starturl, None, x))
    if next_url == 'Nothing found': return 
    else: stock.append(next_url)
        
start = time.time()

async def consumer(queue: asyncio.Queue, stock: List):
    while True:
        soup = await queue.get()
        url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: reformat_book_page_urls(x))
        stock.extend(url)
        queue.task_done()

async def producer(queue: asyncio.Queue, url):
    soup = await get_soup(url)
    await queue.put(soup)

def how_many_pages(soup):
    num = math.floor(int(scrape_item_from_page(soup, '#default > div > div > div > div > form > strong'))/20)
    return 1 if num < 1 else num

async def scrape(url: str):
    queue = asyncio.Queue()
    stock = []
    length = how_many_pages(await get_soup(url))
    urls = [url]
    if (length > 1):
        tasks = [asyncio.create_task(cat_page_url(reformat_cat_page_url(url, i+1), url, urls)) for i in range(length)]
        await gather(*tasks)
    producers = [asyncio.create_task(producer(queue, url)) for url in urls]
    consumers = [asyncio.create_task(consumer(queue, stock)) for _ in range(10)]
    await asyncio.gather(*producers)
    print('done producing')  
    await queue.join()
    for c in consumers:
        c.cancel()
    # print(stock)
    return stock


# asyncio.run(scrape(cat_with_some_pages))

# print('../../../' in '../../../the-lonely-city-adventures-in-the-art-of-being-alone_639/index.html')
    
print(f"took {time.time() - start} seconds")
