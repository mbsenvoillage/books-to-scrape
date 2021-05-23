from urllib import error
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

def get_parsed_html(url: str) -> object:
    error_counter = 0
    try: 
        html = urlopen(url)
        bs = BeautifulSoup(html.read(), 'lxml')
    except HTTPError:
        print(f"Nothing was found at {url}. The page was either deleted, or the URL is incorrect.")
        error_counter += 1
    except URLError:
        print(f"Something is wrong on the server side. Maybe try later.")
        error_counter += 1
    except:
        print(f"Something went wrong while fetching the html page at {url}")
        error_counter += 1
    return None if error_counter > 0 else bs

def get_category(parsed_html: object) -> str:
    if parsed_html == None:
        print("Cannot fetch category for unknown Html page.")
        return 'Unknown'
    else:
        try:
            ul = parsed_html.find('ul', {'class': 'breadcrumb'}).find_all('li')
            category = ul[2].a.text
        except AttributeError:
            print(f"One of the Html tags being searched is non-existent and the book category cannot be retrieved. The Html page structure might have been modified.")
            return 'Unknown'
     
        return category.strip()
        
    
def get_product_info_table(parsed_html: object) -> object:
    if parsed_html == None:
        print("Cannot fetch table for unknown Html page.")
        return None
    else: 
        try:
            table = parsed_html.find('table')
        except Exception as e:
            print(f"Something went wrong. The table could not be retrieved. Error: {e}")
        return table

def html_table_to_dict(parsed_html_table: object) -> dict:
    table_object = {}
    if parsed_html_table == None:
        print("Cannot transform non-existent HTML to object.")
        return table_object
    else: 
        key = ''
        try:
            for idx, string in enumerate(parsed_html_table):
                if idx % 2 == 0:
                    key = string
                    table_object[string] = ''
                else: 
                    table_object[key] = string
        except Exception as e:
            print(f"Something went wrong. The html table containing the product info could not be formatted. Error: {e}")
            return {}
        return table_object



def get_rating(parsed_html: object) -> str:
    ratings = ['one', 'two', 'three', 'four', 'five']
    err = False
    if parsed_html == None:
        print("Cannot fetch table for unknown Html page.")
        err = True
    else:
        try: 
            star = parsed_html.select('.star-rating')
            if (len(star) == 0):
                err = True
            num_of_stars = star[0]['class'][1].lower()       
        except Exception as e:
            print(e)
            err = True
        return '' if err else str(ratings.index(num_of_stars)+1)
        
def get_description(parsed_html: object) -> str:
    description = ''
    if parsed_html == None:
        print("Cannot fetch product description for unknown HTML page")
    else:
        try:
            siblings = parsed_html.find('div', {'id': 'product_description'}).next_siblings
            for sibling in siblings:
                if sibling.name == "p":
                    description = sibling.text
        except Exception as e:
            print(f"Could not get the description. Error: {e}")
        return description