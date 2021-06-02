from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests

def get_page_html(url: str) -> object:
    html = urlopen(url)
    return BeautifulSoup(html.read(), 'lxml')


page = requests.get('http://books.toscrape.com/')
print(page.text)