import asyncio
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

def get_img_file_path(url, upc, file_data):
    if '../../' not in url:
        return 'Image could not be downloaded'
    else:
        full_url = url.replace('../../', baseurl)
        try:
            file_extension = full_url.split('.')[-1]
            filename = f"/{upc}.{file_extension}"
            file_data .append({'url': full_url, 'filename': filename})
            return 'file://' + get_imgs_dir_path() + filename
        except Exception as e:
            logging.error(e)
        return 'An error occurred'


async def get_book_property(property_name, url, soup, file_data):
    selectors = {
        'url': url,
        'title' : scrape_item_from_page(soup, 'h1'),
        'product_description' : scrape_item_from_page(soup, '#content_inner > article > p'),
        'category': scrape_item_from_page(soup, '#default > div > div > ul > li:nth-child(3) > a'),
        'review_rating' : scrape_item_from_page(soup, '#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating', process=lambda x: get_rating(x)),
        'image_url': get_img_file_path(scrape_item_from_page(soup, '#product_gallery > div > div > div > img', process=lambda x: x['src']), scrape_item_from_page(soup, 'table tr:nth-child(1) > td'), file_data),
        'universal_product_code (upc)': scrape_item_from_page(soup, 'table tr:nth-child(1) > td'),
        'price_excluding_tax': scrape_item_from_page(soup, 'table tr:nth-child(3) > td'),
        'price_including_tax': scrape_item_from_page(soup, 'table tr:nth-child(4) > td'),
        'number_available': scrape_item_from_page(soup, 'table tr:nth-child(6) > td', process=lambda x: get_number_available(x.text))}
    return selectors[property_name]


async def scrape(url: str, bookQueue: asyncio.Queue, imageUrlQueue: asyncio.Queue, ordered_property_names=fieldnames) -> object:  
    scrape_dict = {}
    file_data = []
    try:
        soup = await get_soup(url)
        for property_name in ordered_property_names:
            scrape_dict[property_name] = await get_book_property(property_name, url, soup, file_data)
        await imageUrlQueue.put(file_data[0])
    except Exception as e:
        logging.error(e)
        raise
    # stock.append(scrape_dict)
    await bookQueue.put(scrape_dict)
    print(f"bookQueue size {bookQueue.qsize()}")


# asyncio.run(scrape('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', fieldnames))
