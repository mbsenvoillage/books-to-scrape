from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout
import logging

def get_page(url: str):
    res = ''  
    try:
        res = requests.get(url, timeout=2)
        res.raise_for_status()
    except HTTPError as e:
        logging.error(e)
        raise
    except ConnectionError as e:
        logging.error(e)
        raise
    except Timeout as e:
        logging.error(e)
        raise
    except RequestException as e:
        logging.error(e)
        raise
    else:
        return res.content

def get_soup(url):
    bs = ''
    try:
        res = get_page(url)
    except Exception as e:
        raise
    else:
        try:
            html = res.content
            bs = BeautifulSoup(html, 'html.parser')
            assert html != None, "The Beautiful Soup parser returned an empty object" 
        except AssertionError as e:
            logging.error(e)
            raise
        except Exception as e:
            logging.error(e)
            raise
    return bs
