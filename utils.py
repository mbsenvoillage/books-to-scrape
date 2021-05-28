from bs4 import BeautifulSoup
from urllib.request import urlopen

def get_page_html(url: str) -> object:
    html = urlopen(url)
    return BeautifulSoup(html.read(), 'lxml')