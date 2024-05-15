import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
import time

start_time = time.time()

# Carica il file Excel e leggi l'elenco dei siti web
df = pd.read_excel("Imprese.xlsx")
siti_web = df["Website"].tolist()

lock = threading.Lock()

html_list = []
# pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

with open("estensioni.txt", "r") as file:
    estensioni = [line.strip() for line in file]

errore = 0
eccezione = 0
done = 0
time_out = 0
risposte = {}

def format_site(sito):
    sito = sito.replace(" ", "")
    if not any(sito.endswith(ext) for ext in estensioni):
         sito += ".it"
    if not sito.startswith("http://") and not sito.startswith("https://"):
        sito = "http://" + sito
    return sito


def do_request(sito):
    sito = format_site(sito)
    try:
        response = requests.get(sito, timeout=30)
        if response.status_code == 200:
            risposte[sito] = response.status_code
            # html_list.append(response.text)
            #print(f"HTML ottenuto per {sito}")
            global done
            with lock:
                done += 1
        else:
            risposte[sito] = response.status_code
            #print(f"Errore {response.status_code} nel caricare {sito}")
            global errore
            with lock:
                errore += 1
    except requests.exceptions.Timeout:
        #print("Timed out")
        risposte[sito] = "TIMEOUT"
        global time_out
        with lock:
            time_out += 1
    except Exception as e:
        risposte[sito] = str(e)
        #print(f"Eccezione durante il recupero di {sito}: {str(e)}")
        global eccezione
        with lock:
            eccezione += 1


#Initialize ThreadPoolExecutor and use it to call parse_page() in parallel
with ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(do_request, siti_web[:200])

#Tempistiche
print("--- %s seconds ---" % (time.time() - start_time))
print(f"\nRecuperati: {done}\nErrori:{errore}\nTimeout: {time_out}\nEccezioni:{eccezione}")

# Creazione di un DataFrame da un dizionario
df_finale = pd.DataFrame(list(risposte.items()), columns=["Url", "Status"])

# Salvataggio del DataFrame in un file Excel
df_finale.to_excel("risposte.xlsx", index=False)


