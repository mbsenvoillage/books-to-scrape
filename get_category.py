from asyncio.tasks import gather
from typing import List
from urllib.parse import urlparse
import math
from utils import get_soup, scrape_item_from_page
import re
import time
import asyncio

baseurl = 'http://books.toscrape.com/'
catalogue = 'http://books.toscrape.com/catalogue/'
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
    href = arr[0]['href']
    if ('../../../' in href):
        pattern = '../../../'
    elif ('../../' in href):
        pattern = '../../'
    else:
        return [baseurl+el['href'] for el in arr]
    return [el['href'].replace(pattern, catalogue) for el in arr]

async def cat_page_url(url, starturl, queue: asyncio.Queue):
    """Takes the URL of a category page and returns the URL of the next category page, if there is one"""
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: reformat_cat_page_url(starturl, None, x))
    if next_url == 'Nothing found': return 
    else:
        await queue.put_nowait(next_url)
        
async def consumer(queue: asyncio.Queue, outerurl_queue: asyncio.Queue):
    """Retrieves the soup object of a category page from a queue, extracts all the book urls from that page and adds those URLs to an array provided as a dependency"""
    soup = await queue.get()
    urls = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: reformat_book_page_urls(x))   
    for url in urls:
        await outerurl_queue.put(url)
    queue.task_done()


async def producer(outgoingQueue: asyncio.Queue, incomingQueue: asyncio.Queue):
    """Retrieves the URL of a category page from an array and pushes the soup object of that page on another queue"""
    url = await incomingQueue.get()
    soup = await get_soup(url)
    await outgoingQueue.put(soup)
    incomingQueue.task_done()
    
    
def how_many_pages(soup):
    num = math.floor(int(scrape_item_from_page(soup, '#default > div > div > div > div > form > strong'))/20)
    return 1 if num < 1 else num

async def scrape(url: str, outerurl_queue: asyncio.Queue, number_of_books):
    """Produces the URLs of all the books in a category"""
    soup_queue = asyncio.Queue()
    url_queue = asyncio.Queue()
    tasks = []
    length = how_many_pages(await get_soup(url))
    await url_queue.put(url)
    if (length > 1):
        for i in range(length):
            task = asyncio.create_task(cat_page_url(reformat_cat_page_url(url, i+1), url, url_queue))
            tasks.append(task) 
    tasks.extend(asyncio.create_task(producer(soup_queue, url_queue)) for _ in range(number_of_books))
    tasks.extend(asyncio.create_task(consumer(soup_queue, outerurl_queue)) for _ in range(number_of_books))     
    await soup_queue.join()
    await url_queue.join()
    for c in tasks:
        c.cancel()
    await gather(*tasks, return_exceptions=True)      


