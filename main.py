from asyncio.tasks import gather
import get_book, get_category, logging, file_writer, time, sys, asyncio, os
from dotenv import load_dotenv
import resource


def init_logger():
    if not os.path.exists('app.log'):
        with open('app.log', 'w'): pass
    logging.basicConfig(filename='app.log', format='%(asctime)s: Module: %(module)s / Function: %(funcName)s / Level: %(levelname)s => %(message)s')

if __name__ == '__main__':
    file_writer.create_folder('csv')   
    init_logger()
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
    except Exception:
        pass
    load_dotenv()


url = os.getenv('DEFAULT_SCRAPING_URL')

start = time.time()

async def produce_books(url_list, image_url_list):
    """Gets book page url off the url_queue and scrapes the book page"""
    try:
        book_list = await asyncio.wait_for(asyncio.gather(*[get_book.scrape(url, image_url_list) for url in url_list]), timeout=90)
    except asyncio.TimeoutError:
        print('timed out')
    return book_list

async def consume_books(list_of_books):
    """Gets book dict off the book_queue and writes the book info to csv"""
    try:
        for book in list_of_books:
            cat = book['category']
            await file_writer.write_file(f'./csv/{cat}', 'a', book)
    except Exception as e:
        raise(e)

async def consume_image_urls(image_url_list, img_subfolfer):
    """Gets image url off a queue and downloads the image"""
    try:
        await asyncio.gather(*[file_writer.download_image(image_object['url'], image_object['filename'], img_subfolfer) for image_object in image_url_list])
    except Exception as e:
         raise(e)


async def main(url):
    image_url_list = []
    try:
        urls = await asyncio.wait_for(asyncio.gather(get_category.scrape(url, 200)), timeout=20)
        s = await produce_books(urls[0], image_url_list)
        await asyncio.gather(consume_books(s), consume_image_urls(image_url_list, '_'.join(time.ctime().split())))
    except asyncio.TimeoutError:
        print('timed out')
    except Exception as e:
        logging.error(e)
        print("An error occurred")
        exit()
    else:
        print("Scraping done")


asyncio.run(main(url))

print(f"took {time.time() - start} seconds")
