#!/usr/bin/python3

"""This script allows the user to run the application and print the results to the console."""


from mutual_fund import api

BASE_URL = "https://www.moneycontrol.com/mutual-funds/nav/"

urls = (
    BASE_URL + "aditya-birla-sun-life-equity-fund/MAC006",
    BASE_URL + "axis-bluechip-fund-regular-plan/MAA009",
    BASE_URL + "aditya-birla-sun-life-midcap-fund/MBS027",
    BASE_URL
    + "icici-prudential-india-opportunities-fund-regular-plan/MPI4087",
    BASE_URL
    + "aditya-birla-sun-life-retirement-fund-the-30s-plan-direct-growth/MBS3014",
    BASE_URL + "axis-multicap-fund-regular-plan/MAA739",
    BASE_URL + "sbi-focused-equity-fund/MSB059",
)

api(urls)
