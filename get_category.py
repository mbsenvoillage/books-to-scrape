from asyncio.tasks import create_task
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

async def produce_next_page_url(url, starturl, internalQueue: asyncio.Queue):
    internalQueue.put_nowait(url)
    print(internalQueue.qsize())
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, starturl))
    if next_url == 'Nothing found':
        return
    return await produce_next_page_url(next_url, starturl, internalQueue)


async def consume_next_page_url(internalQueue: asyncio.Queue, externalQueue: asyncio.Queue):  
    while True: 
        url = await internalQueue.get()
        if url is None:
            pass
        soup = await get_soup(url)
        externalQueue.put_nowait(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))
        internalQueue.task_done()
     

# start = time.time()

# print( consume_next_page_url(urlwithoutnext))

async def scrape(url, externalQueue: asyncio.Queue):
    internalQueue = asyncio.Queue()
    producers = [asyncio.create_task(produce_next_page_url(url, url, internalQueue))]
    consumers = [asyncio.create_task(consume_next_page_url(internalQueue, externalQueue)) for i in range(3)]
    await asyncio.gather(*producers)
    await internalQueue.join()
    for c in consumers:
        c.cancel()
    # Wait until all worker tasks are cancelled.

# asyncio.run(scrape())
# print("all done")


# print(f"took {time.time() - start} seconds")
