from aiohttp.client_exceptions import ClientError
from bs4 import BeautifulSoup
import logging
import aiohttp
from aiohttp.web import HTTPException

fieldnames = ['url', 'title', 'product_description', 'category', 'review_rating', 'image_url', 'universal_product_code (upc)', 'price_excluding_tax', 'price_including_tax', 'number_available']

baseurl = 'http://books.toscrape.com/'

async def get_page(url: str):
    res = ''  
    try:
        async with aiohttp.ClientSession() as session:
            res = await session.get(url)
            res.raise_for_status()
            content = await res.text()
    except (Exception, HTTPException, ClientError) as e:
        logging.error(e)
        logging.error(f"something is wrong with url {url}")
        raise
    else:
        return content

async def get_soup(url):
    bs = ''
    try:
        res = await get_page(url) #idle time
    except Exception as e:
        raise
    else:
        try:
            bs = BeautifulSoup(res, 'html.parser')
            assert res != None, "The Beautiful Soup parser returned an empty object" 
        except AssertionError as e:
            logging.error(e)
            raise
        except Exception as e:
            logging.error(e)
            raise
        return bs


def scrape_item_from_page(soup, selector, multi=False, process=lambda x: x.text, default="Nothing found"):
    item = ''
    try:
        bs = soup.select(selector) if multi else soup.select_one(selector)
        if not bs:
            return default
        item = process(bs)
    except Exception as e:
        logging.error(f"{e} : could not get item from page")
        raise
    else:
        return item 