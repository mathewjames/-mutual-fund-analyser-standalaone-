"""This script provides all the basic functionality of the application"""


import re
import urllib.request
from functools import reduce
from itertools import combinations
from bs4 import BeautifulSoup
import fund_model


class MutualFund:
    """A class used to represent each mutual fund"""
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return self.__dict__["name"]


def get_snapshot(port_soup):
    """Returns stats of the fund"""
    table = port_soup.find(id="equity_tab1")
    equity_holdings = float(re.findall(r"\d+\.\d+", table.text)[0])
    snapshot = ["equity_holdings", equity_holdings / 100]
    snap = table("td", limit=23)
    for i in snap:
        if i not in snap[2::3]:
            snapshot.append(i.text)
    return dict(zip(*[iter(snapshot)] * 2))


def get_portfolio(port_soup):
    """Returns the stocks invested in by the fund as a dictionary"""
    table = port_soup.find(id="equityCompleteHoldingTable")
    name = 0
    value = 4
    lst = table("td")
    portfolio = {}
    while value < len(lst):
        stock = re.findall(r"\S.+\S", lst[name].text)[0]
        stock_value = float(lst[value].text[:-1])
        portfolio[stock] = stock_value
        name, value = name + 12, value + 12
    return portfolio


def parse(url):
    """Parses the home page and portfolio page of the fund"""
    data = fund_model.in_db(url)
    if data:
        return data
    main_page = urllib.request.urlopen(url).read()
    main_soup = BeautifulSoup(main_page, "lxml")
    fund_name = re.findall(r"(.+) \[", main_soup.title.text)
    fund_name = re.findall(r"(.+) \[", main_soup.title.text)[0]
    table = main_soup.find("table", class_="navdetails")
    aum = float(table.find("span", class_="amt").text[2:-3])
    port_url = main_soup.find(href=re.compile("portfolio-overview")).get("href")
    port_page = urllib.request.urlopen(port_url).read()
    port_soup = BeautifulSoup(port_page, "lxml")
    snapshot = get_snapshot(port_soup)
    portfolio = get_portfolio(port_soup)
    kwargs = {
        "url": url,
        "name": fund_name,
        "aum": aum,
        "snapshot": snapshot,
        "portfolio": portfolio,
    }
    fund_model.write(kwargs)
    return kwargs


def union_or_intersection(x, y, flag):
    """Returns union or intersection based on a flag variable"""
    if not isinstance(x, dict):
        x = x.portfolio

    if not isinstance(y, dict):
        y = y.portfolio

    if flag == "u":
        return {
            stock: x.get(stock, 0) + y.get(stock, 0)
            for stock in set(x).union(y)
        }
    return {stock: min(x[stock], y[stock]) for stock in set(x).intersection(y)}


def get_diff(x, y):
    """Returns set difference of two portfolios"""
    diff = {}
    exclusive = {}

    if not isinstance(y, dict):
        y = y.portfolio

    for stock, value in x.portfolio.items():
        if stock not in y:
            diff[stock] = value
            exclusive[stock] = value
        elif stock in y and (value > y[stock]):
            diff[stock] = value - y[stock]
    print(f"Stocks only in {x.name}, {len(exclusive)}")
    return diff


def get_overlap(lst):
    """Returns percentage of portfolio overlap"""
    overlapping_stocks = reduce(
        lambda x, y: union_or_intersection(x, y, "i"), lst
    )
    ovrlap = sum(overlapping_stocks.values())
    total_stocks = set().union(*[x.portfolio for x in lst])
    print(f"Total no. of stocks in funds: {len(total_stocks)}")
    common_stocks = list(overlapping_stocks.keys())
    print(f"The common stocks are {common_stocks}, {len(common_stocks)}")
    if common_stocks:
        most_common = list(max(overlapping_stocks.items(), key=lambda k: k[1]))
        most_common[1] = round(most_common[1], 2)
        print(
            f"Most common stock is {most_common[0]} which is {most_common[1]}%"
        )
    else:
        print("No stock common to all funds")
    return round(ovrlap, 2)


def api(urls):
    objects = []
    for url in urls:
        fund_obj = MutualFund(parse(url))
        objects.append(fund_obj)

    overlap = get_overlap(objects)
    print(f"Total Overlap: {overlap}%")

    for comb in combinations(objects, 2):
        print(f"{comb[0]} and {comb[1]}")
        overlap = get_overlap(comb)
        print(f"Overlap: {overlap}%")

    obj_number = len(objects)
    if obj_number > 2:
        set_diff_lst = []
        for obj in objects:
            [new_objects] = [
                item
                for item in combinations(objects, obj_number - 1)
                if obj not in item
            ]
            union = reduce(
                lambda x, y: union_or_intersection(x, y, "u"),
                new_objects,
            )
            difference = get_diff(obj, union)
            set_diff_lst.append(difference)

        non_overlapping_stocks = reduce(
            lambda x, y: union_or_intersection(x, y, "u"), set_diff_lst
        )
        total_aum = 100 * obj_number
        partial_overlap = (
            total_aum - sum(non_overlapping_stocks.values())
        ) / total_aum
        print(f"Partial Overlap: {(partial_overlap * 100):.2f}%")
