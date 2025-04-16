import re
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import customtkinter as ct

def scrapeData():
    matchid = matchID.get().strip()

    response = requests.get(f"https://understat.com/match/{matchid}")
    if response.status_code != 200:
        previewText.delete("1.0", "end")
        previewText.insert("end", f"Failed to retrieve data. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    ugly_soup = str(soup)

    match = re.search(r"var shotsData\s*=\s*JSON.parse\('(.*)'\)", ugly_soup)
    if not match:
        previewText.delete("1.0", "end")
        previewText.insert("end", "Could not find shot data.")
        return

    shotsData = match.group(1)
    data = json.loads(shotsData.encode('utf8').decode('unicode_escape'))
    shotsDf = pd.DataFrame(data['h'])

    previewText.delete("1.0", "end")
    previewText.insert("end", shotsDf.head().to_string(index=False))


    return matchid

app = ct.CTk()
app.geometry("700x700")
app.title("Scraper")

matchID = ct.CTkEntry(app, corner_radius=8, width=200, height=30, placeholder_text="Enter Match ID")
matchID.pack(pady=10)

getDataBtn = ct.CTkButton(app, width=120, text="Get Data", command=scrapeData)
getDataBtn.pack(pady=10)

previewText = ct.CTkTextbox(app, width=600, height=400)
previewText.pack(pady=10)

app.mainloop()
