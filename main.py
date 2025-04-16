import re
import requests
import csv
import json
from bs4 import BeautifulSoup
import pandas as pd
from customtkinter import *
import customtkinter as ct
from tkinter import filedialog
from tkinter import ttk

def scrapeData():
    matchid = matchID.get().strip()

    response = requests.get(f"https://understat.com/match/{matchid}")
    if response.status_code != 200:
        clear_table()
        statusLabel.configure(text=f"Failed to retrieve data. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    ugly_soup = str(soup)

    match = re.search(r"var shotsData\s*=\s*JSON.parse\('(.*)'\)", ugly_soup)
    if not match:
        clear_table()
        statusLabel.configure(text="Could not find shot data.")
        return

    shotsData = match.group(1)
    data = json.loads(shotsData.encode('utf8').decode('unicode_escape'))

    global shotsDf
    shotsDf = pd.DataFrame(data['h'] + data['a'])

    show_table(shotsDf)
    statusLabel.configure(text="Data loaded successfully.")

    return matchid

def saveData():
    if 'shotsDf' not in globals():
        statusLabel.configure(text="Please scrape data first before saving.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if file_path:
        shotsDf.to_csv(file_path, index=False)
        statusLabel.configure(text=f"Data saved to {file_path}")

def clear_table():
    for widget in tableFrame.winfo_children():
        widget.destroy()

def show_table(df):
    clear_table()
    tree = ttk.Treeview(tableFrame, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True)

    scrollbar_y = ttk.Scrollbar(tableFrame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(tableFrame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

app = ct.CTk()
app.geometry("1000x700")
app.title("Scraper")
ct.set_appearance_mode("dark")

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
    background="#2b2b2b",
    foreground="white",
    fieldbackground="#2b2b2b",
    rowheight=25,
    font=('Segoe UI', 10)
)

style.configure("Treeview.Heading",
    background="#1f1f1f",
    foreground="white",
    font=('Segoe UI', 10, 'bold')
)

style.map("Treeview",
    background=[("selected", "#3a7bd5")],
    foreground=[("selected", "white")]
)

matchID = ct.CTkEntry(app, corner_radius=8, width=200, height=30, placeholder_text="Enter Match ID")
matchID.pack(pady=10)

getDataBtn = ct.CTkButton(app, width=120, text="Get Data", command=scrapeData)
getDataBtn.pack(pady=5)

saveBtn = ct.CTkButton(app, width=120, text="Save CSV", command=saveData)
saveBtn.pack(pady=5)

tableFrame = ct.CTkFrame(app, width=900, height=500)
tableFrame.pack(pady=10, fill="both", expand=True)

statusLabel = ct.CTkLabel(app, text="", text_color="lightgreen")
statusLabel.pack()

app.mainloop()
