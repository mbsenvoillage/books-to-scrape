from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout
import logging

fieldnames = ['url', 'title', 'product_description', 'category', 'review_rating', 'image_url', 'universal_product_code (upc)', 'price_excluding_tax', 'price_including_tax', 'number_available']

baseurl = 'http://books.toscrape.com/'

def get_page(url: str):
    res = ''  
    try:
        res = requests.get(url, timeout=2) #idle time
        res.raise_for_status()
        res = res.content
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        logging.error(e)
        raise
    else:
        return res

def get_soup(url):
    bs = ''
    try:
        res = get_page(url) #idle time
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