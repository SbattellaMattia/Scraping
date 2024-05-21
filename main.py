import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

start_time = time.time()

KEYWORD = "blockchain"

total = 0
lock_total = threading.Lock()

done = 0
lock_done = threading.Lock()

time_out = 0
lock_time_out = threading.Lock()

errore = 0
lock_errore = threading.Lock()

eccezione = 0
lock_eccezione = threading.Lock()

risposte = {}

second_iteration = False
secondary_links = []

trovati = []
retry = []


def find_keyword(html):
    if KEYWORD in html:
        return True
    else:
        return False


def find_links(html,sito):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    links_to_other_pages = []

    for link in links:
        href = link["href"]
        if href.endswith(".html") or href.endswith(".htm") or href.endswith(".pdf"):
            if not href.startswith("http://") and not href.startswith("https://"):
                href = "https://" + sito
            links_to_other_pages.append(href)
    return links_to_other_pages


def format_site(sito, estensioni):
    sito = sito.replace(" ", "")
    if not any(sito.endswith(ext) for ext in estensioni):
        sito += ".it"
    if not sito.startswith("http://") and not sito.startswith("https://"):
        sito = "http://" + sito
    return sito


def initialize():
    df = pd.read_excel("Imprese.xlsx")
    siti_web = df["Website"].tolist()
    parsed_siti_web = []

    with open("estensioni.txt", "r") as file:
        estensioni = [line.strip() for line in file]

        for sito in siti_web:
            parsed_siti_web.append(format_site(sito, estensioni))
    return parsed_siti_web


def reformat(links):
    for link in links:
        str(list(link).insert(4, "s"))


def do_request(sito):
    global total
    with lock_total:
        total += 1
    try:
        response = requests.get(sito, timeout=30)
        if response.status_code == 200:
            if find_keyword(response.text.lower()):
                # risposte[sito] = response.status_code, True
                trovati.append(sito)
            elif not second_iteration:
                for link in find_links(response.text,sito):
                    if not link in secondary_links:
                        secondary_links.append(link)
            print(f"HTML ottenuto per {sito}")
            global done
            with lock_done:
                done += 1
        else:
            if response.status_code == 403:
                retry.append(sito)
            else:
                risposte[sito] = response.status_code
                global errore
                with lock_errore:
                    errore += 1
    except requests.exceptions.Timeout:
        # print("Timed out")
        risposte[sito] = "TIMEOUT"
        global time_out
        with lock_time_out:
            time_out += 1
    except Exception as e:
        if "HTTPS" in e:
            retry.append(sito)
        else:
            risposte[sito] = str(e)
            global eccezione
            with lock_eccezione:
                eccezione += 1
        # risposte[sito] = str(e)
        # global eccezione
        # with lock_eccezione:
        #     eccezione += 1

def parallel_request(method, list):
    # Initialize ThreadPoolExecutor and use it to call parse_page() in parallel
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(method, list)


siti_web = initialize()
parallel_request(do_request, siti_web[:10])

parallel_request(do_request, retry)

second_iteration = True
parallel_request(do_request, secondary_links)




# Tempistiche
print("--- %s seconds ---" % (time.time() - start_time))
print(f"Totali:\n\t-Iterazioni: {total}\n\t-Siti web: {len(siti_web)}\n\t-Link: {len(secondary_links)}\n\t-Retry: {len(retry)} \nRecuperati: {done}\nErrori:{errore}\nTimeout: {time_out}\nEccezioni non considerate:{eccezione}")

# Creazione di un DataFrame da un dizionario
df_finale = pd.DataFrame(list(risposte.items()), columns=["Url", "Status"])
df_trovati = pd.DataFrame(trovati, columns=["Url"])

# Salvataggio del DataFrame in un file Excel
df_finale.to_excel("risposte.xlsx", index=False)
df_trovati.to_excel("trovati.xlsx", index=False)
