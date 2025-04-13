import re
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import os
from customtkinter import *
import customtkinter as ct

def scrapeData():
    matchid = input("Enter a match id: ")

    response = requests.get(f"https://understat.com/match/{matchid}")
    
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    ugly_soup = str(soup)

    match = re.search(r"var shotsData .*= JSON.parse\('(.*)'\)", ugly_soup)
    if not match:
        print("Could not find shot data.")
        return

    shotsData = match.group(1)
    data = json.loads(shotsData.encode('utf8').decode('unicode_escape'))
    shotsDf = pd.DataFrame(data['h'])
    filename = f"match_{matchid}_shots.csv"
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)
    shotsDf.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")

    return matchid

if __name__ == "__main__":
    scrapeData()

app = ct.CTk()
app.geometry("700x700")
app.title("Scraper")





app.mainloop()