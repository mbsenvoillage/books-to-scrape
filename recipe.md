## Requests

### Error handling 
```
import requests
from requests.exceptions import HTTPError

for url in ['https://api.github.com', 'https://api.github.com/invalid']:
    try:
        response = requests.get(url)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
```

Or a more complete solution

```
try:
    r = requests.get(url,timeout=3)
    r.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)
```

- Where can it go wrong ?
    - anytime you make a request to the server
        - HTTP errors
            - If it times out, you can set a retry, if it still fails after retries, then check underneath
            - If the base URL is unreachable, the program should be stopped, and a message should be printed to the console
            - If a category page is unreachable :
                - If the user only wants to retrieve the books from a category, the program should be stopped and a message should be printed to the console
                - If the user wants to retrieve more than one category, then the unreachable urls should printed to the console
            - If a book's page is unreachable, then the url should be printed to the console
    - anytime you try to retrieve some part of the DOM
        - that part might not exist
            - If it's an element that should be present on the csv file, then a default value should be returned an added to the csv file
            - If it's an element that should not be present on the csv file, then a message with the non existant element at the end of the path should be printed to the console
    

### Retries

```
import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG)

s = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))

s.get("http://httpstat.us/503")
```

https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry


## Logging

### From multiple modules
source: https://docs.python.org/3/howto/logging.html

```
# myapp.py
import logging
import mylib

def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info('Started')
    mylib.do_something()
    logging.info('Finished')

if __name__ == '__main__':
    main()
# mylib.py
import logging

def do_something():
    logging.info('Doing something')
```

- What does `if __name__ == '__main__'` mean ?
    - https://stackoverflow.com/questions/419163/what-does-if-name-main-do

## Multithreading
https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python#:~:text=Python%20doesn't%20allow%20multi,global%20interpreter%20lock%20(GIL).