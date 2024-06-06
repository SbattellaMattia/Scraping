from concurrent.futures import ThreadPoolExecutor
import threading
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from googlesearch import search
import pandas as pd
import requests
from tqdm import tqdm


class Company:
    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url


results = []
lock = threading.Lock()
names = open('scraper/companies.txt').read().split(
    '\n')  # [len(open('urls.txt').readlines()):]


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def search_duckduckgo(name):
    try:
        urls = DDGS().text(name, max_results=1)
        with lock:
            company = Company(name, urls[0]['href'] if len(urls) > 0 else name)
            results.append(company)
    except Exception as e:
        print(e)


for sub_names in tqdm(split(names[:], 100)):
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(search_duckduckgo, sub_names)
    pd.DataFrame([vars(e) for e in results]).to_csv(
        'scraper/output2-2.csv')

# for name in tqdm(names):
#     with open('urls.txt', 'a') as file:
#         url=search_duckduckgo(name)+'\n'
#         file.write(url)
