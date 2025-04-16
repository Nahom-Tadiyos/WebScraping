import re
import requests
import csv
import json
from bs4 import BeautifulSoup
import pandas as pd
from customtkinter import *
import customtkinter as ct
from tkinter import filedialog

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

    global shotsDf
    shotsDf = pd.DataFrame(data['h'] + data['a'])

    previewText.delete("1.0", "end")
    previewText.insert("end", shotsDf.head().to_string(index=False))

    return matchid

def saveData():
    if 'shotsDf' not in globals():
        previewText.delete("1.0", "end")
        previewText.insert("end", "Please scrape data first before saving.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if file_path:
        shotsDf.to_csv(file_path, index=False)
        previewText.delete("1.0", "end")
        previewText.insert("end", f"Data saved to {file_path}")

app = ct.CTk()
app.geometry("700x700")
app.title("Scraper")
ct.set_appearance_mode("dark")

matchID = ct.CTkEntry(app, corner_radius=8, width=200, height=30, placeholder_text="Enter Match ID")
matchID.pack(pady=10)

getDataBtn = ct.CTkButton(app, width=120, text="Get Data", command=scrapeData)
getDataBtn.pack(pady=10)

previewText = ct.CTkTextbox(app, width=600, height=400)
previewText.pack(pady=10)

saveBtn = ct.CTkButton(app, width=120, text="Save CSV", command=saveData)
saveBtn.pack()

app.mainloop()
