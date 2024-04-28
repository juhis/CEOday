#!/usr/bin/env python3

import csv
import os
import sys
import requests


def convert_csv(infile: str, outfile: str, api_token: str) -> str:
    """
    Write a statement csv file otherwise identical to the input file but with EUR amounts of USD transactions added
    Use the api.apilayer.com/exchangerates_data API to get the daily conversion rate
    """
    csv_in = csv.DictReader(open(infile, "r"))
    csv_out = csv.DictWriter(
        open(outfile, "w"), fieldnames=csv_in.fieldnames + ["Amount_EUR"]
    )
    csv_out.writeheader()
    for row in csv_in:
        if (
            row["Amount"] == "Amount"
        ):  # if statement contains multiple currencies, there's more than one header
            row["Amount_EUR"] = "Amount_EUR"
        elif row["Orig currency"] == "USD" and row["Payment currency"] == "USD":
            print(f"https://api.apilayer.com/exchangerates_data/convert?to=EUR&from=USD&amount={abs(float(row['Amount']))}&date={row['Date completed (Europe/Helsinki)']}")
            result = requests.get(
                f"https://api.apilayer.com/exchangerates_data/convert?to=EUR&from=USD&amount={abs(float(row['Amount']))}&date={row['Date completed (Europe/Helsinki)']}",
                {"apikey": api_token},
            )
            eur = float(result.json()["result"])
            if float(row["Amount"]) < 0:
                eur *= -1
            row["Amount_EUR"] = "{:.2f}".format(eur)
        elif (
            row["Orig currency"] == "EUR" and row["Payment currency"] == "USD"
        ):  # USD-to-EUR, use the rate by which the conversion was done
            row["Amount_EUR"] = "{:.2f}".format(-float(row["Orig amount"]))
        else:
            row["Amount_EUR"] = row["Amount"]
        csv_out.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 conv.py csv_file api_token")
        quit(1)
    convert_csv(sys.argv[1], os.path.splitext(sys.argv[1])[0] + "_EUR.csv", sys.argv[2])
