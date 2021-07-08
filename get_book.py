import asyncio, logging, re, os
from utils import get_soup, scrape_item_from_page
from file_writer import get_imgs_dir_path
from dotenv import load_dotenv

load_dotenv()

fieldnames = os.getenv('FIELDNAMES').split(',')
baseurl = os.getenv('BASE_URL')

def get_rating(string) -> str:
    ratings = ['one', 'two', 'three', 'four', 'five']
    num_of_stars = string['class'][1].lower()       
    return str(ratings.index(num_of_stars)+1)

def assemble_image_local_file_path(url: str, upc, file_data) -> str:
    """Generates a local file path for a downloaded picture"""
    full_url = baseurl + url.split('../')[-1]
    try:
        file_extension = full_url.split('.')[-1]
        filename = f"/{upc}.{file_extension}"
        file_data.append({'url': full_url, 'filename': filename})
        return 'file://' + get_imgs_dir_path() + filename
    except Exception as e:
        logging.error(e)
    return 'An error occurred'


async def get_book_property(property_name, url, soup, file_data)-> str:
    """Takes a book property as parameter and returns a string containing the queried book property (scrapes elements from book page)"""
    selectors = {
        'url': url,
        'title' : scrape_item_from_page(soup, 'h1'),
        'product_description' : scrape_item_from_page(soup, '#content_inner > article > p'),
        'category': scrape_item_from_page(soup, '#default > div > div > ul > li:nth-child(3) > a'),
        'review_rating' : scrape_item_from_page(soup, '#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating', process=lambda x: get_rating(x)),
        'image_url': assemble_image_local_file_path(scrape_item_from_page(soup, '#product_gallery > div > div > div > img', process=lambda x: x['src']), scrape_item_from_page(soup, 'table tr:nth-child(1) > td'), file_data),
        'universal_product_code (upc)': scrape_item_from_page(soup, 'table tr:nth-child(1) > td'),
        'price_excluding_tax': scrape_item_from_page(soup, 'table tr:nth-child(3) > td'),
        'price_including_tax': scrape_item_from_page(soup, 'table tr:nth-child(4) > td'),
        'number_available': scrape_item_from_page(soup, 'table tr:nth-child(6) > td', process=lambda x: re.findall(r'\d+',x.text)[0])}
    return selectors[property_name]


async def scrape(url: str, image_url_list, ordered_property_names=fieldnames) -> object:  
    """Scrapes required information from a book page. Pushes book dict and image url to asyncio queues"""
    scrape_dict = {}
    file_data = []
    try:
        soup = await get_soup(url)
        for property_name in ordered_property_names:
            scrape_dict[property_name] = await get_book_property(property_name, url, soup, file_data)
        image_url_list.append(file_data[0])
    except Exception as e:
        logging.error(e)
        raise
    return scrape_dict
