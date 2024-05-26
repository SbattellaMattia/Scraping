import threading
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import PyPDF2
import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup, SoupStrainer

from model.web_page import WebPage, Status

# The keywords to look for in web pages
KEYWORDS = ['blockchain', 'smart contract']
# The timeout of each GET request
TIME_LIMIT = 5
# The limit of recursive analysis of links within pages
DEPTH_LIMIT = 2
# How many thread are being used
NUM_THREADS = 256
start_time = time.time()
web_pages_with_keyword = []
lock_web_pages_with_keyword = threading.Lock()

urllib3.disable_warnings()


def search_keyword(html: str) -> bool:
    """
    The policy to determine whether the site cites the blockchain technology
    :param html: the web page to analyse
    :return: whether the site cites the blockchain technology
    """
    return any(e in html.lower() for e in KEYWORDS)


def find_links(html: str, parent_url: str) -> set:
    """
    List the links found in the provided html page
    :param html: the web page to analyse
    :param parent_url: the url of the web page
    :return: the links found in the page
    """
    links = BeautifulSoup(html, parse_only=SoupStrainer('a'), parser='html.parser', features='lxml').find_all('a',
                                                                                                              href=True)
    valid_links = []

    for link in map(lambda e: e["href"], links):
        if '.' not in link or all(
                e not in link.lower() for e in
                ['.mp3', '.jpg', '.png', '.jpeg', '.gif', '.mp4', '.tiff', '.bmp', '.tif', '.tiff.gz', '.bmpx']):
            if len(link) < 2 or link in parent_url:
                continue
            if link.startswith('http') or link.startswith('www'):
                valid_links.append(link)
            elif not link.startswith('#'):
                valid_links.append(parent_url + ('/' if not link.startswith('/') else '') + link.replace('//', '/'))
    return set(valid_links)


def print_progress() -> None:
    """
    Prints current progress along with ETA
    """
    progress = len(list(filter(lambda it: it.is_done, web_pages))) / len(web_pages)
    print(
        f'{round(progress * 100, 1)}% ({len(web_pages)}) ETA: {round((time.time() - start_time) * (1 - progress) / progress, 2)}sec')


def do_request(web_page: WebPage):
    if web_page.base_url in web_pages_with_keyword:
        web_page.status = Status.NO_MORE_NEEDED
        web_page.has_keyword = True
        return
    try:
        response = requests.get(web_page.url, timeout=TIME_LIMIT, verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'})
        web_page.status = Status.SUCCESS
        web_page.code = response.status_code
        if web_page.is_pdf:
            pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
            web_page.has_keyword = any([search_keyword(page.extract_text()) for page in pdf_reader.pages])
            if web_page.has_keyword:
                with lock_web_pages_with_keyword:
                    web_pages_with_keyword.append(web_page.base_url)
        else:
            body = response.text.split('<body')[1].split('</body>')[0] if all(
                e in response.text for e in ['<body', '</body>']) else str(BeautifulSoup(response.text, 'lxml').body)
            if response.status_code == 200:
                web_page.has_keyword = search_keyword(body)
                # Mark the hierarchy has done
                if web_page.has_keyword:
                    with lock_web_pages_with_keyword:
                        web_pages_with_keyword.append(web_page.base_url)
                # Scan for links
                if web_page.depth < DEPTH_LIMIT:
                    new_links = find_links(body, web_page.url)
                    print(web_page.url, len(new_links))
                    web_pages.extend(list(
                        map(lambda url: WebPage(url, depth=web_page.depth + 1, base_url=web_page.base_url), new_links))[
                                     :])
    except requests.exceptions.Timeout:
        web_page.status = Status.TIMEOUT
    except Exception as e:
        print(web_page.url, str(e))
        web_page.status = Status.ERROR
    print_progress()


if __name__ == '__main__':
    # Retrieving the web pages to analyze
    imprese_df = pd.read_excel('Imprese.xlsx')
    web_pages = list(
        map(lambda url: WebPage(url), set(imprese_df['Website'].tolist()[:])))
    # Request processing with multithreading
    while any(not e.is_done for e in web_pages):
        if NUM_THREADS > 1:
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                executor.map(do_request, list(filter(lambda e: not e.is_done, web_pages)))
        else:
            for e in web_pages:
                do_request(e)
        # Saving analysis result to CSV file
        print('SAVING...')
        pd.DataFrame([vars(e) for e in web_pages]).to_csv(
            'output.csv')

    # Print out stats
    print("--- %s seconds ---" % (time.time() - start_time))
    print(
        f"\nTotali: {len(web_pages)}"
        f"\nSuccess: {len(list(filter(lambda e: e.status == Status.SUCCESS, web_pages)))}"
        f"\nError: {len(list(filter(lambda e: e.status == Status.ERROR, web_pages)))}"
        f"\nTimeout: {len(list(filter(lambda e: e.status == Status.TIMEOUT, web_pages)))}"
        f"\nFound: {len(list(filter(lambda e: e.has_keyword, web_pages)))}"
        f"\nWeb page is down: {len(list(filter(lambda e: e.has_error, web_pages)))}")
