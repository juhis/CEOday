#!/usr/bin/env python3

# stmt = open(sys.argv[1], 'r').readlines()

import csv
import os
import sys
import requests


def convert_csv(infile: str, outfile: str, api_token: str) -> str:
    """
    Write a statement csv file otherwise identical to the input file but with EUR amounts of USD transactions added
    Use the exchangeratesapi.io API to get the daily conversion rate
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
            result = requests.get(
                "http://api.exchangeratesapi.io/v1/{}".format(
                    row["Date completed (Europe/Helsinki)"]
                ),
                {"access_key": api_token},
            )
            rate = result.json()["rates"]["USD"]
            row["Amount_EUR"] = "{:.2f}".format(float(row["Amount"]) / rate)
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
