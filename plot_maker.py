import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn
import requests
import os

italian_regions = ['Abruzzo', 'Basilicata', 'P.A. Bolzano', 'Calabria', 'Campania',
       'Emilia Romagna', 'Friuli Venezia Giulia', 'Lazio', 'Liguria',
       'Lombardia', 'Marche', 'Molise', 'Piemonte', 'Puglia', 'Sardegna',
       'Sicilia', 'Toscana', 'P.A. Trento', 'Umbria', "Valle d'Aosta",
       'Veneto']

seaborn.set_style("dark")

# create directories
if not os.path.isdir("data"):
    os.makedirs("data")
if not os.path.isdir("plots"):
    os.makedirs("plots")
for region in italian_regions:
    if not os.path.isdir("plots/" + region):
        os.makedirs("plots/" + region)

# fetch updated csvs
urls = ["https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"]
for url in urls:
    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode('utf-8')
        with open("data/regioni.csv", "w+") as f:
            f.write(decoded_content)

# auxiliary function
def parse_data(s):
    s = s.split(" ")[0]
    mese = s.split("-")[1]
    giorno = s.split("-")[2]
    
    return giorno + "/" + str(int(mese))

# 0: regione_nuovi/tamponi
# 1: provincia totali e logaritmo totali TODO
plot_type = 0

regioni_csv = pd.read_csv("data/regioni.csv")

for region_name in italian_regions:
    if plot_type == 0:
        # --------------- OBTAIN DATA -------------------------------------
        
        regione_csv = regioni_csv[regioni_csv["denominazione_regione"]==region_name]
        # ottengo gioni
        giorni = list(map(parse_data, regione_csv["data"].values))
        
        # nuovi casi all'interno della regione
        totale_casi = regione_csv["totale_casi"].values
        nuovi_casi_positivi = [totale_casi[0]]
        for g in range(len(totale_casi) - 1):
            nuovi_casi_positivi += [totale_casi[g+1] - totale_casi[g]]
        
        # ottengo il numero dei nuovi tamponi giornalieri
        numero_tamponi = regione_csv["tamponi"].values
        delta_tamponi = [numero_tamponi[0]]
        for g in range(len(numero_tamponi) - 1):
            delta_tamponi += [numero_tamponi[g+1] - numero_tamponi[g]]
        
        # percentuale nuovi_positivi/nuovi_tamponi
        div = lambda x: x[0]/x[1] if 0<(x[0]/x[1])<1 else None
        ratio_nuovi_pos_nuovi_tamp = list(map(div, list(zip(nuovi_casi_positivi, delta_tamponi))))
        
        # --------------- END OBTAIN DATA ---------------------------
        w = 0.3
        fig, ax1 = plt.subplots()
        
        ind = np.arange(len(giorni))
        
        ax1.set_xlabel("Giorni")
        ax1.set_ylabel("Unità")
        bar_pos = ax1.bar(ind+w, nuovi_casi_positivi, color="tab:red", width=w)
        bar_tamp = ax1.bar(ind, delta_tamponi, color="tab:grey", width=w)
        ax1.tick_params(axis='y')
        
        ax1.set_xticks(ind+(w/2))
        ax1.set_xticklabels(giorni)
        ax1.legend( (bar_pos, bar_tamp), ('Nuovi casi positivi', 'Nuovi tamponi') )
        ax1.set_xticks([])
    
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        
        color = 'tab:blue'
        ax2.set_ylabel('Nuovi casi positivi / nuovi tamponi (al giorno)', color=color)  # we already handled the x-label with ax1
        line_perc = ax2.plot(giorni, ratio_nuovi_pos_nuovi_tamp, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        fig.set_size_inches(17, 5)
        plt.title(region_name + ": confronto giornaliero tra nuovi casi positivi e nuovi tamponi")
        
        plt.savefig("plots/" + region_name + "/rapporto_nuovi_casi_tamponi.jpg", dpi=200, bbox_inches='tight')
