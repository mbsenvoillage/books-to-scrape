from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from requests.exceptions import HTTPError, ConnectionError, RequestException, Timeout

def get_page_html(url: str) -> object:
    req = ''
    bs = ''
    try:
        req = requests.get(url, timeout=2)
        req.raise_for_status()
    except HTTPError as e:
        print(e)
        raise
    except ConnectionError as e:
        print(e)
        raise
    except Timeout as e:
        print(e)
        raise
    except RequestException as e:
        print(e)
        raise
    else:
        try:
            html = req.text
            bs = BeautifulSoup(html, 'lxml')
        except Exception as e:
            print(e)
            raise
    return bs



print(get_page_html('http://books.toscrape.com/').prettify())