"""This module acts as an interface between the application and the database."""


import re
import json
import sqlite3
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = "https://www.moneycontrol.com/mutual-funds/nav/"


def write(data):
    """Inserts data into the database"""
    url = data["url"].replace(BASE_URL, "")
    snap = json.dumps(data["snapshot"])
    port = json.dumps(data["portfolio"])

    cur.execute(
        "INSERT INTO Funds (url, name, aum, snapshot, port) VALUES (?, ?, ?, ?, ?)",
        (url, data["name"], data["aum"], snap, port),
    )
    con.commit()


def in_db(url):
    """Checks if the data is present in the database"""
    cur.execute(
        "SELECT * FROM Funds WHERE url = ?", (url.replace(BASE_URL, ""),)
    )
    row = cur.fetchone()
    if row is not None:
        kwargs = {
            "url": url,
            "name": row[1],
            "aum": row[2],
            "snapshot": json.loads(row[3]),
            "portfolio": json.loads(row[4]),
        }
        return kwargs
    return None


def update():
    cur.execute("SELECT url FROM Funds")
    urls = cur.fetchall()
    for url in urls:
        main_page = urllib.request.urlopen(BASE_URL + url[0]).read()
        main_soup = BeautifulSoup(main_page, "lxml")
        name = re.findall(r"(.+) \[", main_soup.title.text)[0]
        cur.execute("UPDATE Funds SET name = ? WHERE url = ?", (name, url[0]))
        con.commit()


con = sqlite3.connect("funds.sqlite")
cur = con.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS Funds(
        url TEXT PRIMARY KEY,
        name TEXT,
        aum REAL,
        snapshot TEXT,
        port TEXT
    )
    """
)
# update()
