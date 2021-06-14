from urllib import error
import logging

from requests.api import get
from utils import get_soup, scrape_item_from_page, fieldnames, baseurl
from file_writer import get_imgs_dir_path

def get_rating(string) -> str:
    ratings = ['one', 'two', 'three', 'four', 'five']
    num_of_stars = string['class'][1].lower()       
    return str(ratings.index(num_of_stars)+1)

def get_number_available(string): 
    num = ''
    for character in string:
        if character.isdigit():
            num += character
    return num

def get_img_file_path(url, upc):
    if '../../' not in url:
        return 'Image could not be downloaded'
    else:
        full_url = url.replace('../../', baseurl)
        try:
            file_extension = full_url.split('.')[-1]
            return 'file://' + get_imgs_dir_path() + f"/{upc}.{file_extension}"
        except Exception as e:
            logging.error(e)
        return 'An error occurred'


def get_book_property(property_name, url, soup):
    upc = scrape_item_from_page(soup, 'table tr:nth-child(1) > td')
    img_url = scrape_item_from_page(soup, '#product_gallery > div > div > div > img', process=lambda x: x['src'])
    selectors = {
        'url': url,
        'title' : scrape_item_from_page(soup, 'h1'),
        'product_description' : scrape_item_from_page(soup, '#content_inner > article > p'),
        'category': scrape_item_from_page(soup, '#default > div > div > ul > li:nth-child(3) > a'),
        'review_rating' : scrape_item_from_page(soup, '#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating', process=lambda x: get_rating(x)),
        'image_url': get_img_file_path(img_url, upc),
        'universal_product_code (upc)': upc,
        'price_excluding_tax': scrape_item_from_page(soup, 'table tr:nth-child(3) > td'),
        'price_including_tax': scrape_item_from_page(soup, 'table tr:nth-child(4) > td'),
        'number_available': scrape_item_from_page(soup, 'table tr:nth-child(6) > td', process=lambda x: get_number_available(x.text))}
    return selectors[property_name]


def scrape(url: str, ordered_property_names=fieldnames) -> object:  
    scrape_dict = {}
    try:
        soup = get_soup(url)
        for property_name in ordered_property_names:
            scrape_dict[property_name] = get_book_property(property_name, url, soup)
    except Exception as e:
        logging.error(e)
        raise
    return scrape_dict


# print(scrape('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', fieldnames))
