import getProductInfo

url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

infos = [
"product_page_url",
"universal_product_code (upc)",
"title",
"price_including_tax",
"price_excluding_tax",
"number_available",
"product_description",
"category",
"review_rating",
"image_url",
]

html = getProductInfo.get_parsed_html(url)


print(getProductInfo.get_title(html))


