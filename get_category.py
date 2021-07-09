from asyncio.tasks import gather
from typing import List
from urllib.parse import urlparse
import math, re, asyncio, os
from utils import get_soup, scrape_item_from_page
from dotenv import load_dotenv

load_dotenv()

baseurl = os.getenv('BASE_URL')
catalogue = os.getenv('CATALOGUE')

def reformat_cat_page_url(url: str, index: int=None, parsed_html: object=None):
    """
    Takes a soup object from a category page, extracts the URL of the next category page, 
    which comes in the form page-{number}.html, and produces a full length URL  
    """
    replace_with = parsed_html['href'] if index is None else f'page-{index}.html'
    return re.sub('[a-z]*.html', replace_with, url)

def reformat_book_page_urls(arr: List):
    """ Takes an array of shortened URLs from href tags, and returns a new array with full length URL"""
    return [catalogue + el['href'].split('../')[-1] for el in arr]

async def cat_page_url(url, starturl, queue: asyncio.Queue):
    """Takes the URL of a category page and returns the URL of the next category page, if there is one"""
    soup = await get_soup(urlparse(url).geturl())
    next_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: reformat_cat_page_url(starturl, None, x))
    if next_url == 'Nothing found': return 
    else:
        await queue.put(next_url)
        
async def consumer(queue: asyncio.Queue, list_of_url):
    """Retrieves the soup object of a category page from a queue, extracts all the book urls from that page and adds those URLs to an array provided as a dependency"""
    try:
        soup = await queue.get()
    except asyncio.CancelledError:
        return
    else:
        urls = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: reformat_book_page_urls(x))   
        for url in urls:
            list_of_url.append(url)
        queue.task_done()
        


async def producer(outgoing_queue: asyncio.Queue, incoming_queue: asyncio.Queue):
    """Retrieves the URL of a category page from an array and pushes the soup object of that page on another queue"""
    try:
        url = await incoming_queue.get()
    except asyncio.CancelledError:
        return
    else:
        soup = await get_soup(url)
        await outgoing_queue.put(soup)
        incoming_queue.task_done()
    
    
def how_many_pages(soup):
    """Calculates the number of pages in a category. Takes BS object as param"""
    num = math.floor(int(scrape_item_from_page(soup, '#default > div > div > div > div > form > strong'))/20)
    return 1 if num < 1 else num

async def scrape(url: str, number_of_books):
    """Produces the URLs of all the books in a category. Pushes book page urls to an asyncio queue"""
    soup_queue = asyncio.Queue(maxsize=100)
    url_queue = asyncio.Queue(maxsize=100)
    list_of_urls = []
    tasks = []
    length = how_many_pages(await get_soup(url))
    await url_queue.put(url)
    if (length > 1):
        for i in range(length):
            task = asyncio.create_task(cat_page_url(reformat_cat_page_url(url, i+1), url, url_queue))
            tasks.append(task) 
    tasks.extend(asyncio.create_task(producer(soup_queue, url_queue)) for _ in range(number_of_books))
    tasks.extend(asyncio.create_task(consumer(soup_queue, list_of_urls)) for i in range(number_of_books))   
    for completed in asyncio.as_completed([*tasks]):
        await completed
        break 
    await soup_queue.join()
    await url_queue.join()
    for c in tasks:
        c.cancel()
    await gather(*tasks, return_exceptions=True) 
    return list_of_urls
         
