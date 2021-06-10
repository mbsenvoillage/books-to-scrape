from urllib import error
import logging
from utils import get_soup, scrape_item_from_page

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
        
def scrape(url: str) -> object:  
    scrape_dict = {}
    try:
        soup = get_soup(url)
        scrape_dict['url'] = url
        scrape_dict['title'] = scrape_item_from_page(soup, 'h1')
        scrape_dict['product_description'] = scrape_item_from_page(soup, '#content_inner > article > p')
        scrape_dict['category'] = scrape_item_from_page(soup, '#default > div > div > ul > li:nth-child(3) > a')
        scrape_dict['review_rating'] = scrape_item_from_page(soup, '#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating.Two', process=lambda x: get_rating(x))
        scrape_dict['image_url'] = scrape_item_from_page(soup, '#product_gallery > div > div > div > img', process=lambda x: x['src'])
        scrape_dict['universal_product_code (upc)'] = scrape_item_from_page(soup, 'table tr:nth-child(1) > td')
        scrape_dict['price_excluding_tax'] = scrape_item_from_page(soup, 'table tr:nth-child(3) > td')
        scrape_dict['price_including_tax'] = scrape_item_from_page(soup, 'table tr:nth-child(4) > td')
        scrape_dict['number_available'] = scrape_item_from_page(soup, 'table tr:nth-child(6) > td', process=lambda x: get_number_available(x.text))
    except Exception as e:
        logging.error(e)
        raise
    return scrape_dict

print(scrape('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'))