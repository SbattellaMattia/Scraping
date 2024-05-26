from concurrent.futures import ThreadPoolExecutor

from googlesearch import search

results = []
names = open('companies.txt').read().split('\n')[len(open('urls.txt').readlines()):]


def get_url(name):
    urls = list(search(name, num_results=3, sleep_interval=0))
    print(round(len(results) / len(names) * 100, 2), '%')
    results.append(urls[0] if len(urls) > 0 else name)


with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(get_url, names)

with open('urls.txt', 'a') as file:
    file.write('\n'.join(results))
