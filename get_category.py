from asyncio.tasks import gather
from typing import List
from urllib.parse import urlparse
import math
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
    """
    Takes a soup object from a category page, extracts the URL of the next category page, 
    which comes in the form page-{number}.html, and produces a full length URL  
    """
    replace_with = parsed_html['href'] if index is None else f'page-{index}.html'
    return re.sub('[a-z]*.html', replace_with, url)
  
def reformat_book_page_urls(arr: List):
    """ Takes an array of shortened URLs from href tags, and returns a new array with full length URL"""
    pattern = '../../../' if '../../../' in arr[0]['href'] else '../../'
    return [el['href'].replace(pattern, baseurl) for el in arr]

async def cat_page_url(url, starturl, queue: asyncio.Queue):
    """Takes the URL of a category page and returns the URL of the next category page, if there is one"""
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: reformat_cat_page_url(starturl, None, x))
    if next_url == 'Nothing found': return 
    # else: stock.append(next_url)
    else:
        await queue.put_nowait(next_url)
    print(f'urlQueue size after put: {queue.qsize()}')
        
start = time.time()

async def consumer(queue: asyncio.Queue, outerUrlQueue: asyncio.Queue):
    """Retrieves the soup object of a category page from a queue, extracts all the book urls from that page and adds those URLs to an array provided as a dependency"""
    soup = await queue.get()
    urls = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: reformat_book_page_urls(x))
    # stock.extend(url)
    for url in urls:
        await outerUrlQueue.put(url)
    print(f'soupQueue size after get: {queue.qsize()}')
    queue.task_done()

async def producer(outgoingQueue: asyncio.Queue, incomingQueue: asyncio.Queue):
    """Retrieves the URL of a category page from an array and pushes the soup object of that page on another queue"""
    url = await incomingQueue.get()
    soup = await get_soup(url)
    print(f'length of urlQueue {incomingQueue.qsize()}')
    await outgoingQueue.put(soup)
    print(f'length of soupQueue {outgoingQueue.qsize()}')
    incomingQueue.task_done()
    

def how_many_pages(soup):
    num = math.floor(int(scrape_item_from_page(soup, '#default > div > div > div > div > form > strong'))/20)
    return 1 if num < 1 else num

async def scrape(url: str, outerUrlQueue: asyncio.Queue):
    """Produces the URLs of all the books in a category"""
    soupQueue = asyncio.Queue()
    urlQueue = asyncio.Queue()
    tasks = []
    # stock = []
    length = how_many_pages(await get_soup(url))
    await urlQueue.put(url)
    if (length > 1):
        for i in range(length):
            task = asyncio.create_task(cat_page_url(reformat_cat_page_url(url, i+1), url, urlQueue))
            tasks.append(task)
    tasks.extend(asyncio.create_task(producer(soupQueue, urlQueue)) for _ in range(500))
    # tasks.extend(asyncio.create_task(consumer(soupQueue, stock)) for _ in range(100))  
    tasks.extend(asyncio.create_task(consumer(soupQueue, outerUrlQueue)) for _ in range(500))  
    await soupQueue.join()
    await urlQueue.join()
    for c in tasks:
        c.cancel()
    await gather(*tasks, return_exceptions=True)   
    # return stock

# s = []
# asyncio.run(scrape(cat_with_many_pages, []))

# print('../../../' in '../../../the-lonely-city-adventures-in-the-art-of-being-alone_639/index.html')
    
print(f"took {time.time() - start} seconds")
