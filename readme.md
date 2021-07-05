# Purpose
books-to-scrape is a short program used to scrape pages from www.books.toscrape.com. The scraping targets the books for sale on the website. 
Here is the list of information retrieved for each book : 
- Title
- Price
- Description
- UPC
- Price
- Number of books available
- Book image
- Category

Each book belongs to a category, and a csv file is generated for each category. That file includes all the info listed above.
Images are stored in a separate directory and named after the book's UPC.

# Requirements

This program will work for versions of Python from 3.8 and above. You will need the package installer [pip](https://pypi.org/project/pip/) and [virtualenv](https://pypi.org/project/virtualenv/#description) if you want to create an isolated environment for this project. 

# Installation 

You will first need to clone this repo. Then just run from inside the downloaded `pip install -r requirements.txt`

# Usage

To scrape all books from the website you can run `python3 main.py`