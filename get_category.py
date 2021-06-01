from urllib import error
import logging
from utils import get_page_html
from urllib.error import URLError

def get_list_of_categories(parsed_html: object):
    ul = parsed_html.find('ul', {'class': 'nav'})
    return ul