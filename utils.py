from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout
import logging

def get_page_html(url: str) -> object:
    req = ''
    bs = ''
    try:
        req = requests.get(url, timeout=2)
        req.raise_for_status()
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
        try:
            req.encoding = 'utf-8'
            html = req.text
            bs = BeautifulSoup(html, 'lxml')
        except Exception as e:
            logging.error(e)
            raise
    return bs


def is_page_scrapable(url: str) -> object:
    try:
        html = get_page_html(url)
        assert html != None, "The Beautiful Soup parser returned an empty object"  
    except AssertionError as e:
        logging.error(e)
        raise
    except Exception as e:
        logging.error(e)
        raise
    else:
        return html