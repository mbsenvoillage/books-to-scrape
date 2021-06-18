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

async def next_page_url(url, arr: List, starturl):
    arr.append(url)
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, starturl))
    if next_url == 'Nothing found':
        return arr
    return await next_page_url(next_url, arr, starturl)

async def cat_page_url(url, starturl, stock):
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, starturl))
    if next_url == 'Nothing found':
        return
    stock.append(next_url)

# async def scrape(url: str):  
#     category_page_urls = await next_page_url(url, [], url)
#     list_of_url = []
#     for url in category_page_urls:
#         soup = await get_soup(url)
#         list_of_url.extend(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))
#     return list_of_url

start = time.time()

async def consumer(queue: asyncio.Queue, stock: List):
    while True:
        soup = await queue.get()
        url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x))
        stock.extend(url)
        queue.task_done()
        # return url

async def producer(queue: asyncio.Queue, url):
    soup = await get_soup(url)
    await queue.put(soup)
     

async def scrape(url:string):
    queue = asyncio.Queue()
    stock = []
    baseurl = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    soup = await get_soup(baseurl)
    num = math.floor(int(scrape_item_from_page(soup, '#default > div > div > div > div > form > strong'))/20)
    length = 1 if num < 1 else num
    tasks = []
    urls = []
    for i in range(length):
        task = asyncio.create_task(cat_page_url(f'http://books.toscrape.com/catalogue/category/books_1/page-{i+1}.html', baseurl, urls))
        tasks.append(task)
    await gather(*tasks)
    urls.append(baseurl)
    producers = [asyncio.create_task(producer(queue, url)) for url in urls]
    consumers = [asyncio.create_task(consumer(queue, stock)) for _ in range(10)]
    await asyncio.gather(*producers)
    print('done producing')  
    await queue.join()
    for c in consumers:
        c.cancel()
    print(stock)
    
  
    

asyncio.run(main())


print(f"took {time.time() - start} seconds")
