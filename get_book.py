from urllib import error
import logging
from utils import get_page_html
from urllib.error import URLError

logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

def get_category(parsed_html: object) -> str:
    ul = parsed_html.find('ul', {'class': 'breadcrumb'}).find_all('li')
    category = ul[2].a.text  
    return category.strip()
            
def get_table(parsed_html: object) -> object:
    table = {}
    td = parsed_html.findAll('td')
    table['universal_product_code (upc)'] = td[0].text
    table['price_excluding_tax'] = td[2].text
    table['price_including_tax'] = td[3].text
    num = ''
    for character in td[5].text:
        if character.isdigit():
            num += character
    table['number_available'] = num
    return table
 

def get_rating(parsed_html: object) -> str:
    ratings = ['one', 'two', 'three', 'four', 'five']
    star = parsed_html.select('.star-rating')
    num_of_stars = star[0]['class'][1].lower()       
    return str(ratings.index(num_of_stars)+1)
        
def get_description(parsed_html: object) -> str:
    description = ''    
    siblings = parsed_html.find('div', {'id': 'product_description'}).next_siblings
    for sibling in siblings:
        if sibling.name == "p":
            description = sibling.text 
    return description

def get_title(parsed_html: object) -> str:
    return parsed_html.find('h1').text   

def get_picture_url(parsed_html: object) -> str:
    return parsed_html.find('img')['src']

def is_page_scrapable(url: str) -> object:
    try:
        html = get_page_html(url)
        assert html != None, "The Beautiful Soup parser returned an empty object"
    except URLError as e :
        logging.error(f"{e} - URL: {url}.")
        raise   
    except AssertionError as e:
        logging.error(e)
        raise
    else:
        return html

def scrape(url: str) -> object:
    scrape_dict = {}
    html = is_page_scrapable(url)
    try:
        for key, value in get_table(html).items():
            scrape_dict[key] = value
        scrape_dict['url'] = url
        scrape_dict['title'] = get_title(html)
        scrape_dict['product_description'] = get_description(html)
        scrape_dict['category'] = get_category(html)
        scrape_dict['review_rating'] = get_rating(html)
        scrape_dict['image_url'] = get_picture_url(html)
    except (AttributeError, KeyError) as e:
        logging.error(e)
        raise
    except Exception as e:
        logging.error(e)
        raise
    return scrape_dict