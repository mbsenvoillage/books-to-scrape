from urllib.parse import urlparse
import logging
from utils import get_soup, scrape_item_from_page
import re


baseurl = 'http://books.toscrape.com/catalogue/'
urlwithnext= 'http://books.toscrape.com/catalogue/category/books/childrens_11/index.html'
urlwithoutnext = 'http://books.toscrape.com/catalogue/category/books/self-help_41/index.html'
cat_with_many_pages = 'http://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'

def get_page_book_list(parsed_html: object):
    return parsed_html.find('ol', {'class', 'row'})

def get_next_page_url(parsed_html: object, url: str): 
    return re.sub('[a-z]*.html', parsed_html['href'], url)

soup = get_soup(urlwithnext)
#print(utils.scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, urlwithnext)))

def get_link(arr):
    array = []
    for el in arr:
        array.append(el['href'].replace('../../../', baseurl))
    return array

#print(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))


def get_all_category_pages_url(url):
    category_page_urls = []
    category_page_urls.append(url)
    soup = get_soup(url)
    next_page_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, url))
    if next_page_url:
        category_page_urls.append(next_page_url)
        while next_page_url != 'Nothing found':
            soup = get_soup(urlparse(next_page_url).geturl())
            next_page_url = scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a', process=lambda x: get_next_page_url(x, url))
            if next_page_url != 'Nothing found':
                category_page_urls.append(next_page_url)
    return category_page_urls

#print(get_all_category_pages_url(urlwithnext))


def scrape(url: str):  
    category_page_urls = get_all_category_pages_url(url)
    list_of_url = []
    for url in category_page_urls:
        soup = get_soup(url)
        list_of_url.extend(scrape_item_from_page(soup, '#default > div > div > div > div > section > div:nth-child(2) > ol > li > article > h3 > a', multi=True, process=lambda x: get_link(x)))
    return list_of_url

# print(scrape(cat_with_many_pages))
