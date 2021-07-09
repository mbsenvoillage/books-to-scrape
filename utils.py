from aiohttp.client_exceptions import ClientError
from bs4 import BeautifulSoup
import logging, aiohttp, os, asyncio
from aiohttp.web import HTTPException
from dotenv import load_dotenv
from aiohttp.resolver import AsyncResolver

load_dotenv()
fieldnames = os.getenv('FIELDNAMES')





async def get_page(url: str, semaphore):
    """Takes URL as parameter and returns the response object from request"""
    res = ''  
    try:
        resolver = AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])
        connector = aiohttp.TCPConnector(limit=0, resolver=resolver)  # need unlimited connections
        async with aiohttp.ClientSession(connector=connector) as session:
            async with semaphore, session.get(url) as res:
                res.raise_for_status()
                content = await res.text()
    except (Exception, HTTPException, ClientError) as e:
        logging.error(e)
        logging.error(f"something is wrong with url {url}")
        raise
    else:
        return content

async def get_soup(url: str, semaphore):
    """Takes URL as parameter and returns a BeautifulSoup object"""
    bs = ''
    try:
        res = await get_page(url, semaphore) 
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
    """Takes a BS object, a CSS selector, a boolean, a function and a string as parameters and returns an element scraped off the webpage corresponding to the BS object"""
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
